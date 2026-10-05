import io
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from pypdf import PdfReader
from backend.app.main import app
from backend.app.calculations.takeoff import takeoff
from backend.app.calculations.legacy import year1_inputs, calculate_discounted_lcc, REPL_CONV, REPL_SUST
from backend.app.schemas.models import Project
from backend.app.services.analysis import scenarios, compute_periods

client = TestClient(app)


def sample():
    return client.get('/api/demo').json()


def test_original_legacy_engine_and_adapter_match():
    c, s = year1_inputs(220, 6.6, True, 528000, 580800)
    expected = calculate_discounted_lcc(528000, 580800, c, s, replacements_conv=REPL_CONV, replacements_sust=REPL_SUST)
    result = client.post('/api/analyse', json=client.get('/api/demo?legacy=true').json()).json()['periods']['40']
    assert result['break_even_year'] == 37
    assert result['savings_aud'] == pytest.approx(2986.6845689938636, abs=.001)
    assert result['conventional']['total_lcc'] == pytest.approx(expected['total_lcc_conv'], abs=.001)
    assert result['sustainable']['cashflows'][1]['operating'] == pytest.approx(4278.94, abs=.01)
    assert result['conventional']['cashflows'][1]['operating'] == pytest.approx(6546.66, abs=.01)
    assert sum(row['replacement'] for row in result['conventional']['cashflows']) == 5300


def test_takeoff_worked_example_and_overrides():
    q = takeoff(220, 1, 2)['quantities']
    assert round(q['perimeter_m'], 1) == 60.6
    assert round(q['gross_wall_area_m2'], 1) == 163.5
    assert round(q['net_wall_area_m2'], 1) == 117.9
    assert q['glazing_area_m2'] == pytest.approx(39.6)
    assert q['roof_area_m2'] == pytest.approx(253)
    assert q['light_points'] == 55 and q['taps'] == 6
    assert takeoff(220, 2, 2)['quantities']['max_solar_kw'] == pytest.approx(10.12)
    assert takeoff(220, 1, 2, overrides={'roof_area_m2': 100})['quantities']['max_solar_kw'] == 8


def test_no_measures_and_code_required_are_identical():
    for patch_values in ({'selected_measures': []}, {'selected_measures': ['insulation'], 'code_required_measures': ['insulation']}):
        response = client.post('/api/analyse', json=sample() | patch_values)
        assert response.status_code == 200, response.text
        assert response.json()['periods']['40']['savings_aud'] == pytest.approx(0, abs=1e-9)


def test_quotes_interactions_and_contributions_reconcile():
    p = sample() | {'price_overrides': {'solar_pv': 1000}, 'selected_measures': ['insulation', 'glazing', 'hvac', 'solar_pv', 'smart_controls'], 'disposal_sustainable': 40000}
    result = client.post('/api/analyse', json=p).json()
    assert next(m for m in result['measures'] if m['id'] == 'solar_pv')['premium'] == 1000
    assert next(m for m in result['measures'] if m['id'] == 'solar_pv')['badge'] == 'Your price'
    for n, r in result['periods'].items():
        assert sum(r['component_savings'].values()) == pytest.approx(r['savings_aud'], abs=1e-7)
        assert sum(m['marginal_savings'] for m in result['measure_contributions'][n]) == pytest.approx(r['savings_aud'], abs=1e-7)
    rows = result['measures']
    assert all(m['labour_added'] == m['margin_added'] == m['gst_added'] == 0 for m in rows)
    assert any(abs(m['interaction_adjustment']) > 1 for m in result['measure_contributions']['40'])


@pytest.mark.parametrize('measure', ['insulation','glazing','airtightness_shading','hvac','hot_water','solar_pv','rainwater','water_fixtures','lighting','smart_controls','sustainable_materials'])
def test_every_measure_is_finite_and_end_uses_nonnegative(measure):
    result = client.post('/api/analyse', json=sample() | {'selected_measures': [measure], 'price_overrides': {'sustainable_materials': 1000} if measure == 'sustainable_materials' else {}}).json()
    assert result['periods']['40']['conventional']['total_lcc'] > 0
    assert result['energy']['grid_kwh'] >= 0 and result['energy']['water_kl'] >= 0
    assert result['energy']['self_use_kwh'] <= sum(result['energy']['sustainable_end_uses'].values()) + 1e-9


def test_literature_hand_calculation_reducible_usage_only():
    p = Project.model_validate(sample() | {'mode': 'literature', 'sustainable_cost': None, 'energy_reduction': .3, 'water_reduction': .4, 'maintenance_reduction': .2})
    rates = dict(electricity_rate=.3, electricity_daily=1, water_rate=3, water_fixed=900)
    c, s, a = scenarios(p, rates)
    result = compute_periods(c, s, a)['30']
    premium = c.capital * p.premium
    expected = -premium
    for year in range(1, 31):
        expected += (p.energy_kwh * .3 * .3 * 1.03 ** year + p.water_kl * .4 * 3 * 1.025 ** year + c.maintenance * .2 * 1.025 ** year) / 1.05 ** year
    assert result['savings_aud'] == pytest.approx(expected, abs=.01)
    payload = client.post('/api/analyse', json=p.model_dump(mode='json')).json()
    assert set(payload['literature_scenarios']) == {'Low','Mid','High'}


def test_validation_roof_unknown_and_required_terminal():
    p = sample()
    for update in ({'selected_measures':['unknown']}, {'terminal_confirmed':False}, {'area':30,'selected_measures':['solar_pv'],'solar_kw':13.2}, {'price_overrides':{'solar_pv':-5}}):
        assert client.post('/api/analyse', json=p | update).status_code == 422


def test_stateless_hosted_report_and_chat_need_no_saved_files(monkeypatch, tmp_path):
    monkeypatch.setenv('VERCEL','1')
    with patch('httpx.post', side_effect=AssertionError('No external calls')):
        result = client.post('/api/analyse', json=sample()).json()
        assert not list(tmp_path.rglob('*.json'))
        assert client.get('/api/analyses/' + result['id']).status_code == 404
        snapshot = {'project':result['project'],'rates':result['rates'],'years':40}
        assert client.post('/api/report',json=snapshot).status_code == 200
        pdf = client.post('/api/report/pdf',json=snapshot)
        assert pdf.status_code == 200, pdf.text[:200]
        reader = PdfReader(io.BytesIO(pdf.content))
        assert len(reader.pages) >= 3
        text = ''.join(p.extract_text() for p in reader.pages)
        assert 'GREENCOST SYDNEY' in text and 'Complete input record' in text
        assert all(len(p.extract_text().split()) > 20 for p in reader.pages)
        answer = client.post('/api/chat',json=snapshot | {'question':'What if discount is 7%?'}).json()
        assert 'what_if' in answer
        assert client.post('/api/knowledge/pdf',content=b'%PDF').status_code == 403


def test_share_snapshot_reproduces_tariffs_after_cache_change():
    result = client.post('/api/analyse',json=sample()).json()
    with patch('backend.app.agent.workflow.tariffs',side_effect=AssertionError('Use snapshot')):
        shared = client.post('/api/analyse',json=result['project'] | {'rates_snapshot':result['rates']}).json()
    assert shared['periods']['40']['savings_aud'] == result['periods']['40']['savings_aud']


def test_origin_payload_limits_and_path_traversal():
    assert client.post('/api/analyse',json=sample(),headers={'Origin':'https://evil.example'}).status_code == 403
    assert client.post('/api/analyse',content=b' ' * (256 * 1024 + 1)).status_code == 413
    assert client.get('/api/analyses/not-a-uuid').status_code == 404
    assert client.post('/api/analyse',json=sample() | {'rates_snapshot':{'electricity_rate':1}}).status_code == 422
