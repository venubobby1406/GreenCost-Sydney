from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from backend.app.schemas.models import Project
from backend.app.rag.store import retrieve
from backend.app.research.sources import tariffs, load_sources
from backend.app.services.analysis import scenarios, assumptions, compute_periods, compute_sensitivity
from backend.app.services.explanation import explain
from backend.app.research.web import research


class State(TypedDict, total=False):
    raw: dict
    project: Project
    evidence: list
    web_calls: int
    web_status: str
    rates: dict
    scenarios: tuple
    periods: dict
    sensitivity: list
    result: dict


def validate_input(state):
    return {"project": Project.model_validate(state["raw"])}


def retrieve_local_evidence(state):
    p = state["project"]
    return {
        "evidence": retrieve(
            f"{p.building_type} {' '.join(p.features)} building lifespan discount rate energy water maintenance sustainable premium",
            4,
            "PROJECT_RESEARCH",
        )
    }


def research_online(state):
    p = state["project"]
    evidence, calls, status = research(
        f"NSW {p.building_type} {' '.join(p.features)} sustainable building energy water maintenance guidance",
        p.web_research,
    )
    return {"evidence": state["evidence"] + evidence, "web_calls": calls, "web_status": status}


def check_data(state):
    return {"rates": tariffs(state["project"])}


def calculate_scenarios(state):
    return {"scenarios": scenarios(state["project"], state["rates"])}


def calculate_lcc(state):
    return {"periods": compute_periods(*state["scenarios"])}


def sensitivity_analysis(state):
    return {"sensitivity": compute_sensitivity(*state["scenarios"])}


def generate_explanation(state):
    p = state["project"]
    calls = 0
    gemini_status = "not_requested"
    for key, result in state["periods"].items():
        paragraphs, n, status = explain(result, allow_llm=int(key) == p.years,
                                        evidence=state["evidence"], project=p.model_dump(mode="json"))
        if int(key) == p.years:
            gemini_status = status
        result["explanation"] = paragraphs
        calls += n
    c, s, _ = state["scenarios"]
    confidence = (
        "Low / indicative"
        if p.input_quality == "demo"
        else "High"
        if p.input_quality == "actual"
        and p.performance_source == "user"
        and p.tariff_mode == "official"
        and p.sustainable_cost is not None
        else "Medium"
    )
    reasons = {
        "Low / indicative": "Demo costs, consumption, service lives and research performance assumptions have not been validated for a real building.",
        "Medium": "One or more cost, performance or tariff inputs remain estimates or research assumptions.",
        "High": "User declares actual capital and consumption with project performance and applicable official tariffs; independently verify the inputs.",
    }
    return {
        "result": dict(
            project=p.model_dump(mode="json"),
            periods=state["periods"],
            sensitivity=state["sensitivity"],
            assumptions=assumptions(p, state["rates"], c, s),
            rates=state["rates"],
            sources=load_sources(),
            evidence=state["evidence"],
            confidence=confidence,
            confidence_reason=reasons[confidence],
            usage=dict(tavily_calls=state.get("web_calls", 0), llm_calls=calls),
            research_status=dict(gemini=gemini_status, tavily=state.get("web_status", "disabled"), vector_db="chroma"),
            limitations=[
                "Academic scenario model; no QS quote, building simulation or regulatory certificate.",
                "Same building geometry in both scenarios. Feature toggles do not invent individual savings; entered reductions represent the whole package and avoid double counting.",
                "Nominal AUD cash flows, year-zero capital; year t prices escalate t times and year-end costs discount t times. Use mutually consistent nominal rates.",
                "Flat electricity tariff only; grid imports are entered net of solar self-use. Export income, batteries, gas, finance, land, grants and taxes are excluded unless included explicitly in inputs.",
                "Replacements occur before the terminal year, never at retirement. No residual value is inferred; user supplies it.",
                "Sydney Water fixed charges normalized from 92 days to 365 days; confirm metering, drought tariff, wastewater and stormwater applicability.",
                "Discounted break-even is the first crossover and may later reverse. Long-term tariffs are escalated scenarios, not official future prices.",
                "Research PDFs are secondary evidence; their claims and bibliography have not been independently peer-reviewed.",
            ],
        )
    }


builder = StateGraph(State)
nodes = [
    validate_input,
    retrieve_local_evidence,
    research_online,
    check_data,
    calculate_scenarios,
    calculate_lcc,
    sensitivity_analysis,
    generate_explanation,
]
for node in nodes:
    builder.add_node(node.__name__, node)
builder.add_edge(START, nodes[0].__name__)
for a, b in zip(nodes, nodes[1:]):
    builder.add_edge(a.__name__, b.__name__)
builder.add_edge(nodes[-1].__name__, END)
workflow = builder.compile()


def analyse(raw):
    return workflow.invoke({"raw": raw})["result"]


STAGES = {
    "validate_input": "Your project is validated",
    "retrieve_local_evidence": "Relevant PDF passages retrieved from Chroma",
    "research_online": "Web research checked",
    "check_data": "Utility prices validated",
    "calculate_scenarios": "Both building scenarios prepared",
    "calculate_lcc": "Annual cash flows calculated",
    "sensitivity_analysis": "Sensitivity scenarios calculated",
    "generate_explanation": "Your explanation is ready",
}


def analyse_stream(raw):
    for update in workflow.stream({"raw": raw}, stream_mode="updates"):
        for node, values in update.items():
            message = STAGES[node]
            if node == "research_online" and values.get("web_status") != "complete":
                message = "Web research skipped or unavailable; continuing with local PDF evidence"
            if node == "generate_explanation" and values["result"]["research_status"]["gemini"] != "complete":
                message = "Calculated explanation ready; Gemini was not used successfully"
            yield dict(type="stage", stage=node, message=message)
            if "result" in values:
                yield dict(type="result", result=values["result"])
