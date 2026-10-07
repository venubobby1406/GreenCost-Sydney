import json
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.pdf_report import pdf_report
from pypdf import PdfReader
import io

client = TestClient(app)


def sample(**changes):
    return client.get('/api/demo').json() | changes


def test_every_stream_stage_has_start_and_completion_and_actual_provider_status():
    response = client.post('/api/analyse/stream', json=sample(web_research=False))
    events = [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith('data: ')]
    starts = [e['stage'] for e in events if e['type'] == 'stage_start']
    completed = [e['stage'] for e in events if e['type'] == 'stage']
    assert starts == completed
    assert len(starts) == 8
    for stage in starts:
        assert next(i for i, e in enumerate(events) if e['type'] == 'stage_start' and e['stage'] == stage) < next(i for i, e in enumerate(events) if e['type'] == 'stage' and e['stage'] == stage)
    assert events[-2]['providers']['gemini'] == 'not_configured'
    assert events[-1]['result']['research_status']['gemini'] == 'not_configured'


def test_retained_building_has_no_terminal_removal_and_rejects_conflicting_amounts():
    assert client.post('/api/analyse', json=sample(end_of_life_mode='retained', disposal_conventional=1)).status_code == 422
    result = client.post('/api/analyse', json=sample(end_of_life_mode='retained', disposal_conventional=0, disposal_sustainable=0, residual_conventional=0, residual_sustainable=0)).json()
    assert result['periods']['40']['conventional']['components']['disposal'] == 0
    assert result['periods']['40']['sustainable']['components']['residual'] == 0


def test_apartment_unit_cannot_take_whole_building_shared_upgrades():
    for feature in ['solar_pv', 'rainwater', 'airtightness_shading']:
        assert client.post('/api/analyse', json=sample(building_type='Apartment', selected_measures=[feature])).status_code == 422
    assert client.post('/api/analyse', json=sample(building_type='Apartment', selected_measures=['water_fixtures'])).status_code == 200


def test_water_units_and_maintenance_labels_in_export_are_consistent():
    result = client.post('/api/analyse', json=sample(water_kl=500, selected_measures=[])).json()
    water = next(a for a in result['assumptions'] if a['name'] == 'Annual water')
    assert water['value'] == 500000 and water['unit'] == 'L/year'
    million = next(a for a in result['assumptions'] if a['name'] == 'Annual water in million litres')
    assert million['value'] == .5
    text = '\n'.join(p.extract_text() for p in PdfReader(io.BytesIO(pdf_report(result, 40))).pages)
    assert '500,000 L (0.5 million litres)' in text
    assert 'Initial building cost' in text
    assert 'Routine maintenance over 40 years' in text


def test_removal_estimate_matches_supported_house_scope_and_has_no_invented_salvage():
    p = sample(area=200, floors=1, end_of_life_mode='estimate', disposal_conventional=26000,
               disposal_sustainable=26000, residual_conventional=0, residual_sustainable=0)
    assert client.post('/api/v1/preview', json=p).status_code == 200
    for changes in [{'area':300}, {'building_type':'Commercial / Other'}, {'residual_sustainable':500}]:
        assert client.post('/api/v1/preview', json=p | changes).status_code == 422
