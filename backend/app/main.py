import csv
import io
import json
import re
import os
import hashlib
import logging
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
logger = logging.getLogger("greencost")
from backend.app.services.security import guard
app.middleware("http")(guard)


@app.get("/api/health")
def health():
    rag = readiness()
    return {"status": "ok", "rag_ready": rag["ready"], "knowledge": rag, "vector_db": "none",
            "uploads_enabled": not bool(os.getenv("VERCEL")),
            "gemini_configured": configured(), "tavily_configured": bool(os.getenv("TAVILY_API_KEY")),
            "gemini_model": os.getenv("GEMINI_MODEL", "gemini-2.5-flash")}


@app.get("/api/demo")
def demo(legacy: bool = False):
    p = json.loads((DATA / "demo/sydney_house.json").read_text(encoding="utf-8"))
    p.update(mode="itemised", selected_measures=["insulation", "solar_pv", "rainwater"], sustainable_cost=None,
             terminal_confirmed=True, disposal_conventional=33000, disposal_sustainable=33000,
             web_research=False, energy_kwh=5200, water_kl=200, maintenance_fraction=.005,
             maintenance_annual=None, replacements=[])
    if legacy:
        p.update(name="Legacy study fixture (not a current new home)", mode="literature", preset="legacy_6star",
                 area=220, floors=1, conventional_cost=528000, sustainable_cost=580800,
                 water_escalation=.02, maintenance_escalation=.015, other_annual=0, replacements=[],
                 features=["solar", "insulation", "rainwater", "durable"], disposal_conventional=0, disposal_sustainable=0,
                 residual_conventional=0, residual_sustainable=0, tariff_mode="user", electricity_rate=.325,
                 electricity_daily=1.5, water_rate=3.41, water_fixed_annual=987.16,
                 tariff_note="Original legacy regression fixture; historical indicative rates, not current official tariffs")
    return Project.model_validate(p).model_dump(mode="json")


@app.post("/api/v1/validate")
def validate_project(project: Project):
    return project.model_dump(mode="json")


@app.get("/health")
def health_alias():
    return health()


@app.get("/api/v1/measures")
def measures():
    from backend.app.services.catalogue import catalogue
    return catalogue()


@app.get("/api/v1/assumptions")
def regional_assumptions():
    root = DATA / "regions/sydney_nsw"
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in root.glob("*.json")}


@app.post("/api/v1/preview")
def preview(raw: dict):
    from backend.app.services.catalogue import measure_costs
    try:
        p = Project.model_validate(raw | {"terminal_confirmed": True})
        rows, geometry = measure_costs(p)
        return dict(measures=rows, takeoff=geometry, premium=sum(m["premium"] for m in rows))
    except (ValueError, ValidationError) as error:
        raise HTTPException(422, str(error)) from error


@app.post("/api/v1/takeoff")
def takeoff_endpoint(project: Project):
    from backend.app.calculations.takeoff import takeoff
    from backend.app.calculations.lcc import area_m2
    try:
        return takeoff(area_m2(project.area, project.area_unit), project.floors, project.bathrooms,
                       project.solar_kw, project.tank_kl, project.quantity_overrides)
    except ValueError as error:
        raise HTTPException(422, str(error)) from error


@app.get("/api/sources")
def sources():
    return load_sources()


@app.post("/api/analyse")
@app.post("/api/v1/calculate/lcc")
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
            logger.exception("Analysis workflow failed")
            yield 'data: {"type":"error","message":"Analysis could not finish. Check the backend logs and retry."}\n\n'
    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.post("/api/knowledge/pdf")
async def upload_pdf(request: Request, filename: str = "research.pdf"):
    if os.getenv("VERCEL"):
        raise HTTPException(403, "Hosted research library is read-only. Add PDFs locally, index them, then redeploy.")
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
    target.parent.mkdir(parents=True, exist_ok=True)
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
    return chat_result(result, request)


def chat_result(result, request):
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


# Hosted routes rebuild the calculation from validated inputs and captured rates.
# They require no server persistence and never accept client-supplied totals.
from backend.app.schemas.models import StrictModel, Money
from pydantic import Field, model_validator
from typing import Literal


class Snapshot(StrictModel):
    project: Project
    rates: dict[str, Money]
    years: Literal[30, 40, 50] = 40

    @model_validator(mode="after")
    def complete_rates(self):
        if set(self.rates) != {"electricity_rate", "electricity_daily", "water_rate", "water_fixed"}:
            raise ValueError("A snapshot requires all four utility rates.")
        if self.project.mode == "itemised":
            from backend.app.services.catalogue import measure_costs
            measure_costs(self.project)
        return self


class SnapshotQuestion(Snapshot):
    question: str = Field(min_length=1, max_length=500)


def rebuild(snapshot):
    raw = snapshot.project.model_dump(mode="json") | {"rates_snapshot": snapshot.rates, "web_research": False}
    project = Project.model_validate(raw)
    from backend.app.agent import workflow as engine
    state = {"raw": project.model_dump(mode="json")}
    # Exporting and deterministic what-ifs never spend an AI request.
    for node in engine.nodes[:-1]:
        if node is engine.research_online:
            state.update(evidence=state["evidence"], web_calls=0, web_status="disabled")
        else:
            state.update(node(state))
    from backend.app.services.explanation import explain
    for key, result in state["periods"].items():
        result["explanation"] = explain(result, allow_llm=False)[0]
    c, s, _ = state["scenarios"]
    from backend.app.services.analysis import assumptions, research_outputs
    return dict(id="device-snapshot", created_at=project.price_date.isoformat(), project=project.model_dump(mode="json"),
                periods=state["periods"], sensitivity=state["sensitivity"], rates=snapshot.rates,
                assumptions=assumptions(project, snapshot.rates, c, s), sources=load_sources(), evidence=state["evidence"],
                confidence="Indicative", confidence_reason="Rebuilt from captured inputs and utility rates.",
                limitations=engine.LIMITATIONS,
                **research_outputs(project, snapshot.rates, state["periods"]))


@app.post("/api/report", response_class=HTMLResponse)
def stateless_report(snapshot: Snapshot):
    return HTMLResponse(report_html(rebuild(snapshot), snapshot.years))


@app.post("/api/chat")
def stateless_chat(snapshot: SnapshotQuestion):
    return chat_result(rebuild(snapshot), ChatRequest(question=snapshot.question, years=snapshot.years))


@app.post("/api/report/pdf")
@app.post("/api/v1/report/pdf")
def stateless_pdf(snapshot: Snapshot):
    from backend.app.services.pdf_report import pdf_report
    return Response(pdf_report(rebuild(snapshot), snapshot.years), media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="GreenCost-{snapshot.years}-year-report.pdf"'})


@app.post("/api/v1/sensitivity/matrix")
def stateless_sensitivity(snapshot: Snapshot):
    return rebuild(snapshot)["sensitivity"]


@app.post("/api/v1/narrative/explain")
def stateless_explanation(snapshot: Snapshot):
    return {"explanation": rebuild(snapshot)["periods"][str(snapshot.years)]["explanation"], "mode": "calculated"}
