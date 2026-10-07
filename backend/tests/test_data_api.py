import json
from copy import deepcopy
from datetime import date
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from backend.app.schemas.models import Project
from backend.app.research.sources import DATA, load_sources, tariffs, validate_source
from backend.app.main import app
from backend.app.rag.store import retrieve, ingest

client = TestClient(app)


def demo():
    return json.loads((DATA / "demo/sydney_house.json").read_text(encoding="utf-8"))


def test_source_policy():
    source = deepcopy(next(s for s in load_sources() if s["id"] == "aer_2026_27"))
    source["effective_from"] = "2025-07-01"
    with pytest.raises(ValueError):
        validate_source(source, date(2026, 10, 2))
    source["effective_from"] = "2026-07-01"
    source["url"] = "https://aer.gov.au.evil.example/prices"
    with pytest.raises(ValueError):
        validate_source(source, date(2026, 10, 2))


def test_ppi_units():
    source = deepcopy(next(s for s in load_sources() if s["id"] == "abs_ppi_2026"))
    source["values"]["building_construction"]["unit"] = "AUD/m²"
    with pytest.raises(ValueError):
        validate_source(source, date(2026, 10, 2))


def test_stale_and_future_sources():
    source = deepcopy(next(s for s in load_sources() if s["id"] == "aer_2026_27"))
    with pytest.raises(ValueError):
        validate_source(source, date(2027, 7, 1))
    with pytest.raises(ValueError):
        validate_source(source, date(2026, 6, 1))


def test_zone_not_guessed():
    d = demo()
    del d["zone"]
    with pytest.raises(ValidationError):
        Project.model_validate(d)


def test_commercial_rejects_residential_tariffs():
    d = demo() | {"building_type": "Commercial / Other"}
    with pytest.raises(ValidationError):
        Project.model_validate(d)


def test_fixed_daily_water():
    p = Project.model_validate(demo())
    rates = tariffs(p)
    assert rates["water_fixed"] == pytest.approx((26.65 + 189.88) / 92 * 365)


def test_no_fabricated_cost_or_invalid_inputs():
    for update in ({"conventional_cost": None}, {"energy_kwh": -1}, {"discount": float("nan")}, {"area": 0}):
        with pytest.raises(ValidationError):
            Project.model_validate(demo() | update)


def test_offline_full_workflow():
    with (
        patch("httpx.post", side_effect=AssertionError("No external calls")),
        patch.dict("os.environ", {"GEMINI_API_KEY": "", "TAVILY_API_KEY": ""}),
    ):
        response = client.post("/api/analyse", json=demo())
        assert response.status_code == 200, response.text
        result = response.json()
        assert len(result["sensitivity"]) == 48
        assert result["usage"] == {"tavily_calls": 0, "llm_calls": 0}
        assert result["periods"]["40"]["conventional"]["total_lcc"] > 0
        assert result["periods"]["40"]["savings_aud"] < 0  # no forced sustainability win
        assert result["evidence"]
        id = result["id"]
        report = client.get(f"/api/analyses/{id}/report")
        assert report.status_code == 200 and "<svg" in report.text
        assert "complete input record" in report.text
        assert client.get(f"/api/analyses/{id}/cashflows").status_code == 200
        answer = client.post(
            f"/api/analyses/{id}/chat", json={"question": "What if electricity rises 5% per year?"}
        ).json()
        assert "what_if" in answer
        assert answer["what_if"]["conventional"]["total_lcc"] > result["periods"]["40"]["conventional"]["total_lcc"]


def test_incremental_index():
    assert ingest()["new_embeddings"] == 0
    docs = retrieve("life cycle discount rate", 4, "PROJECT_RESEARCH")
    assert docs and all(d["source_type"] == "PROJECT_RESEARCH" and d["page"] > 0 for d in docs)


def test_report_escapes_project_input():
    r = client.post("/api/analyse", json=demo() | {"name": "<script>alert(1)</script>"}).json()
    html = client.get(f"/api/analyses/{r['id']}/report").text
    assert "<script>" not in html


def test_detailed_mode():
    p = demo() | {
        "cost_mode": "detailed",
        "detailed_complete": True,
        "materials": [
            {
                "name": "Concrete",
                "quantity": 80,
                "unit": "m³",
                "unit_cost": 300,
                "service_life": None,
                "replacement_interval": None,
                "maintenance": 100,
            }
        ],
        "other_construction": 500000,
    }
    r = client.post("/api/analyse", json=p).json()
    assert r["periods"]["40"]["conventional"]["components"]["capital"] == 524000
