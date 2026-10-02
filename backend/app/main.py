import csv
import io
import json
import re
import os
import hashlib
from pypdf import PdfReader
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, Response, StreamingResponse
from starlette.concurrency import run_in_threadpool
from pydantic import ValidationError
from backend.app.schemas.models import Project, ChatRequest
from backend.app.agent.workflow import analyse, analyse_stream
from backend.app.research.sources import DATA, load_sources
from backend.app.rag.store import retrieve, readiness, ingest
from backend.app.services import storage
from backend.app.services.explanation import money, answer_question
from backend.app.services.gemini import configured
from backend.app.services.report import report_html

app = FastAPI(title="GreenCost Sydney", version="1.0.0")


@app.get("/api/health")
def health():
    rag = readiness()
    return {"status": "ok", "rag_ready": rag["ready"], "knowledge": rag, "vector_db": "chroma",
            "gemini_configured": configured(), "tavily_configured": bool(os.getenv("TAVILY_API_KEY")),
            "gemini_model": os.getenv("GEMINI_MODEL", "gemini-3.5-flash")}


@app.get("/api/demo")
def demo():
    return json.loads((DATA / "demo/sydney_house.json").read_text(encoding="utf-8"))


@app.get("/api/sources")
def sources():
    return load_sources()


@app.post("/api/analyse")
def analysis(project: Project):
    try:
        return storage.save(analyse(project.model_dump(mode="json")))
    except (ValueError, ValidationError) as error:
        raise HTTPException(422, str(error)) from error


@app.post("/api/analyse/stream")
def stream_analysis(project: Project):
    def events():
        try:
            for event in analyse_stream(project.model_dump(mode="json")):
                if event["type"] == "result":
                    event = dict(type="result", result=storage.save(event["result"]))
                yield "data: " + json.dumps(event) + "\n\n"
        except (ValueError, ValidationError) as error:
            yield "data: " + json.dumps(dict(type="error", message=str(error))) + "\n\n"
        except Exception:
            yield 'data: {"type":"error","message":"Analysis could not finish. Check the backend logs and retry."}\n\n'
    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.post("/api/knowledge/pdf")
async def upload_pdf(request: Request, filename: str = "research.pdf"):
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(422, "Choose a PDF document.")
    raw = bytearray()
    async for part in request.stream():
        raw.extend(part)
        if len(raw) > 10 * 1024 * 1024:
            raise HTTPException(413, "PDFs must be smaller than 10 MB.")
    try:
        reader = PdfReader(io.BytesIO(raw))
        if reader.is_encrypted or len(reader.pages) > 200 or not any(page.extract_text() for page in reader.pages):
            raise ValueError("Use a text-based, unlocked PDF with at most 200 pages.")
    except Exception as error:
        raise HTTPException(422, "Use a readable, text-based, unlocked PDF with at most 200 pages.") from error
    name = re.sub(r"[^a-zA-Z0-9._-]", "_", Path(filename).stem)[:70] or "research"
    target = DATA / "knowledge" / (name + "_" + hashlib.sha256(raw).hexdigest()[:12] + ".pdf")
    existed = target.exists()
    target.write_bytes(raw)
    try:
        result = await run_in_threadpool(ingest)
    except Exception as error:
        if not existed:
            target.unlink(missing_ok=True)
        raise HTTPException(503, "The PDF could not be indexed. Check the knowledge-base configuration.") from error
    return dict(filename=target.name, **result)


def saved(id):
    result = storage.get(id)
    if not result:
        raise HTTPException(404, "Analysis not found")
    return result


@app.get("/api/analyses/{id}")
def read(id: str):
    return saved(id)


@app.get("/api/analyses/{id}/report", response_class=HTMLResponse)
def report(id: str, years: int = 40, download: bool = True):
    if years not in (30, 40, 50):
        raise HTTPException(422, "Select 30, 40 or 50 years")
    return HTMLResponse(
        report_html(saved(id), years),
        headers={"Content-Disposition": f'attachment; filename="GreenCost-{years}-year-report.html"'}
        if download
        else {},
    )


@app.get("/api/analyses/{id}/cashflows")
def cashflows(id: str, years: int = 40):
    if years not in (30, 40, 50):
        raise HTTPException(422, "Select 30, 40 or 50 years")
    r = saved(id)["periods"][str(years)]
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(
        [
            "scenario",
            "year",
            "energy",
            "water",
            "maintenance",
            "replacement",
            "other",
            "disposal",
            "residual",
            "nominal_total",
            "pv_total",
            "cumulative_pv",
        ]
    )
    for scenario in ("conventional", "sustainable"):
        for row in r[scenario]["cashflows"]:
            writer.writerow(
                [scenario]
                + [
                    row[k]
                    for k in (
                        "year",
                        "energy",
                        "water",
                        "maintenance",
                        "replacement",
                        "other",
                        "disposal",
                        "residual",
                        "nominal_total",
                        "pv_total",
                        "cumulative_pv",
                    )
                ]
            )
    return Response(
        out.getvalue(), media_type="text/csv", headers={"Content-Disposition": 'attachment; filename="cashflows.csv"'}
    )


@app.post("/api/analyses/{id}/chat")
def chat(id: str, request: ChatRequest):
    result = saved(id)
    q = request.question.lower()
    citations = retrieve(q, 4) + [e for e in result.get("evidence", []) if e.get("source_type") == "WEB_RESEARCH"][:3]
    matches = list(re.finditer(r"(?<![\w.])([+-]?\d+(?:\.\d+)?)\s*%", q))
    match = matches[0] if len(matches) == 1 else None
    parameter = (
        "energy_escalation"
        if any(w in q for w in ("electricity", "energy"))
        and any(w in q for w in ("rise", "rises", "escalat", "increase", "growth"))
        else "discount"
        if "discount" in q
        else None
    )
    if match and "discount" in q and any(w in q for w in ("energy", "electricity")):
        match = None
    if match and parameter:
        raw = result["project"] | {
            parameter: float(match.group(1)) / 100,
            "years": request.years or result["project"]["years"],
        }
        try:
            p = Project.model_validate(raw)
            # Reuse deterministic graph, disable optional explanation call for chat.
            from backend.app.services.analysis import scenarios, compute_periods
            from backend.app.research.sources import tariffs

            r = compute_periods(*scenarios(p, result.get("rates") or tariffs(p)))[str(p.years)]
            return {
                "answer": f"Recalculated over {p.years} years at {match.group(1)}% {parameter.replace('_', ' ')}: conventional {money(r['conventional']['total_lcc'])}; sustainable {money(r['sustainable']['total_lcc'])}; signed savings {money(r['savings_aud'])}. This what-if does not overwrite your saved analysis.",
                "citations": citations,
                "what_if": r,
            }
        except (ValueError, ValidationError):
            return {
                "answer": "That rate is outside the supported range. Use the financial assumptions form for a valid scenario.",
                "citations": [],
            }
    if any(w in q for w in ("what if", "what happens", "change", "increase", "decrease", "reduce", "%")):
        answer = "I can recalculate questions such as “What if electricity rises 5% per year?” or “What if the discount rate is 7%?”. For other numerical changes, edit the project inputs and analyse again."
    elif any(w in q for w in ("initial", "capital", "premium")):
        answer = "The sustainable capital input is either your explicit quote or the conventional cost plus the selected research premium. That premium is an editable assumption, not an official Sydney construction rate."
    elif "discount" in q:
        answer = "Discounting gives less present weight to later costs. Increasing it typically reduces the value of future operating savings compared with the upfront premium. Replacement timing can also change the comparison."
    elif any(w in q for w in ("electricity", "tariff", "rate come")):
        answer = (
            "The cached AER source contains residential flat-rate DMO caps for your explicitly selected distribution zone, effective July 2026 through June 2027. These are reference caps; your retail plan may differ."
            if result["project"]["tariff_mode"] == "official"
            else "This analysis uses the utility rates and source note you supplied in the project form."
        )
    elif "water" in q:
        answer = "The model reduces variable water usage only. Applicable fixed water, wastewater and stormwater service charges remain unchanged between scenarios and escalate at the selected water rate."
    elif any(w in q for w in ("basix", "regulat", "sepp")):
        answer = "Residential BASIX and non-residential Sustainable Buildings SEPP requirements depend on the development. This comparison is not a compliance assessment and does not translate BASIX targets into electricity savings."
    else:
        answer = "Local research citations are listed below. Ask about capital costs, discounting, water charges, electricity sources or an electricity-escalation what-if. Retrieved documents cannot change calculation rules."
    if not any(w in q for w in ("what if", "what happens", "change", "increase", "decrease", "reduce", "%")):
        generated, calls, status = answer_question(request.question, result, request.years or result["project"]["years"], citations)
        if generated:
            answer = generated
        return {"answer": answer, "citations": citations, "llm_calls": calls, "gemini_status": status}
    return {"answer": answer, "citations": citations}
