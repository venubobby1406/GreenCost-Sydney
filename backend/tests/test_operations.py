from dataclasses import replace
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services import budget, storage, security
from backend.app.calculations.lcc import Scenario, Assumptions, compare
from scripts.update_sources import refresh

client = TestClient(app)


def test_provider_budget_stops_and_no_network_when_offline(monkeypatch):
    monkeypatch.setenv('TAVILY_DAILY_CAP','1')
    assert budget.reserve('tavily') is True
    assert budget.reserve('tavily') is False
    with patch('httpx.Client', side_effect=AssertionError('No network')):
        assert refresh(offline=True)['tavily_calls'] == 0
        assert refresh(direct=True)['tavily_calls'] == 0


def test_atomic_json_storage_and_invalid_id(tmp_path):
    record = storage.save({'project':{'name':'Test'}})
    assert storage.get(record['id']) == record
    assert storage.get('../../secret') is None
    assert not list(tmp_path.rglob('*.tmp'))
    assert list(tmp_path.rglob('*.json'))
    assert not list(tmp_path.rglob('*.sqlite*'))


def test_rate_limit_and_recovery_message(monkeypatch):
    monkeypatch.setenv('REQUESTS_PER_MINUTE','1')
    monkeypatch.setattr(security,'_requests',{})
    project = client.get('/api/demo').json()
    assert client.post('/api/v1/validate', json=project).status_code == 200
    response = client.post('/api/v1/validate', json=project)
    assert response.status_code == 429 and response.headers['Retry-After'] == '60'


def test_higher_discount_reduces_savings_for_positive_future_saving_stream():
    c = Scenario(1000, 200, 20, 30, .3, 1, 2, 100)
    s = replace(c, capital=1010, energy_kwh=100, water_kl=10, maintenance=20)
    savings = [compare(c,s,Assumptions(40,r,0,0,0,0,0))['savings_aud'] for r in (.04,.05,.06,.07)]
    assert savings == sorted(savings,reverse=True)


def test_gas_usage_reduction_keeps_fixed_charge():
    from backend.app.schemas.models import Project
    from backend.app.services.analysis import scenarios
    p = Project.model_validate(client.get('/api/demo').json() | {'mode':'literature','gas_mj':10000,'gas_rate':.04,'gas_daily':.5,'gas_note':'User bill'})
    rates = dict(electricity_rate=.3,electricity_daily=1,water_rate=3,water_fixed=900)
    c,s,_ = scenarios(p,rates)
    assert c.gas_annual == pytest.approx(582.5)
    assert s.gas_annual == pytest.approx(10000*(1-p.energy_reduction)*.04+182.5)


def test_incomplete_snapshot_and_bad_geometry_return_validation_error():
    p = client.get('/api/demo').json()
    assert client.post('/api/report',json={'project':p,'rates':{'electricity_rate':1}}).status_code == 422
    p['quantity_overrides'] = {'not_a_quantity':1}
    rates = dict(electricity_rate=.3,electricity_daily=1,water_rate=3,water_fixed=900)
    assert client.post('/api/report',json={'project':p,'rates':rates}).status_code == 422


def test_legacy_rejects_ignored_physical_and_tariff_edits():
    p = client.get('/api/demo?legacy=true').json()
    for update in ({'electricity_rate': .5}, {'tariff_mode': 'official'}, {'other_annual': 500},
                   {'rates_snapshot': dict(electricity_rate=.5,electricity_daily=1.5,water_rate=3.41,water_fixed=987.16)}):
        assert client.post('/api/v1/validate', json=p | update).status_code == 422


def test_chunked_body_is_bounded_without_content_length():
    def parts():
        for _ in range(5):
            yield b' ' * 65536
    assert client.post('/api/v1/validate', content=parts(), headers={'Content-Type':'application/json'}).status_code == 413


def test_corrupt_budget_stops_provider_without_breaking_calculator(monkeypatch):
    path = budget.DATA / 'prices' / 'usage.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('{invalid', encoding='utf-8')
    assert budget.reserve('tavily') is False
    monkeypatch.setenv('GEMINI_DAILY_CAP','not-an-integer')
    assert budget.reserve('gemini') is False
    assert client.post('/api/analyse', json=client.get('/api/demo').json()).status_code == 200
