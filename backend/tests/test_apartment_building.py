"""Whole-building inputs must never double-count area or reuse unit scope."""
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.schemas.models import Project
from backend.app.services.analysis import scenarios
from backend.app.services.occupancy import apartment_occupancy
from backend.app.research.sources import tariffs

client = TestClient(app)


def building(**changes):
    demo = client.get('/api/demo').json()
    return demo | dict(building_type='Apartment Building', area_basis='per_floor',
        entered_area=500, area=10000, floors=20, occupants=3, occupant_mode='estimate',
        apartment_average_unit_m2=75, apartment_residential_share=.8,
        tariff_mode='user', electricity_rate=.3, electricity_daily=50,
        water_rate=3.4, water_fixed_annual=30000, tariff_note='Aggregate building meters',
        conventional_cost=30000000, energy_kwh=300000, water_kl=10000,
        selected_measures=[], web_research=False) | changes


def validated(**changes):
    response = client.post('/api/v1/validate', json=building(**changes))
    assert response.status_code == 200, response.text
    return response.json()


def test_per_floor_area_and_occupants_are_verified_on_server():
    assert validated()['occupants'] == 219
    assert validated(floors=50, area=25000)['occupants'] == 547
    assert client.post('/api/v1/validate', json=building(area=500)).status_code == 422
    assert client.post('/api/v1/validate', json=building(entered_area=None)).status_code == 422


def test_total_area_is_not_multiplied_again_and_manual_count_is_preserved():
    for floors in (4, 20, 50):
        p = validated(area_basis='total', entered_area=10000, floors=floors)
        assert p['area'] == 10000 and p['occupants'] == 219
    assert validated(occupant_mode='manual', occupants=300)['occupants'] == 300
    assert validated(floors=50, area=25000, occupant_mode='manual', occupants=300)['occupants'] == 300


def test_area_units_and_editable_density_assumptions():
    assert validated(area_unit='ft²', entered_area=500/.092903, area=10000/.092903)['occupants'] == 219
    assert validated(apartment_average_unit_m2=100)['occupants'] == apartment_occupancy(10000,100,.8)['occupants']
    assert validated(apartment_residential_share=.6)['occupants'] < 219
    for field, value in [('apartment_average_unit_m2', 0), ('apartment_residential_share', 0), ('floors',101)]:
        assert client.post('/api/v1/validate', json=building(**{field:value})).status_code == 422


def test_whole_building_requires_aggregate_project_tariffs():
    assert client.post('/api/v1/validate', json=building(tariff_mode='official')).status_code == 422
    p = Project.model_validate(building(conventional_cost=None, cost_per_m2=3000))
    rates = tariffs(p)
    assert rates['electricity_daily'] == 50 and rates['water_fixed'] == 30000
    c, _, _ = scenarios(p, rates)
    assert c.capital == 30000000  # 10,000 m² × 3,000; never × 20 again.


def test_analysis_and_replay_keep_area_and_occupancy_assumptions():
    response = client.post('/api/analyse', json=building())
    assert response.status_code == 200, response.text
    result = response.json()
    assert result['project']['occupants'] == 219
    rows = {a['name']:a for a in result['assumptions']}
    assert rows['Number of occupants']['value'] == 219
    assert rows['Number of floors']['value'] == 20
    assert rows['Entered area per floor']['value'] == 500
    assert rows['Area']['value'] == 10000
    assert any('lifts' in text for text in result['limitations'])
    import io
    from pypdf import PdfReader
    from backend.app.services.pdf_report import pdf_report
    document = PdfReader(io.BytesIO(pdf_report(result,40)))
    text = '\n'.join(page.extract_text() for page in document.pages)
    assert 'Number of occupants' in text and '219' in text
    assert 'Entered area per floor' in text
    assert 'lifts' in text
    replay = client.post('/api/analyse', json=result['project'])
    assert replay.status_code == 200, replay.text
    assert replay.json()['periods'] == result['periods']


def test_blank_drafts_and_legacy_apartment_scope():
    raw = building(area=None, entered_area=None, floors=None, occupants=None,
        apartment_average_unit_m2=None, apartment_residential_share=None)
    response = client.post('/api/v1/draft', json=raw)
    assert response.status_code == 200, response.text
    assert response.json()['occupants'] is None
    assert client.post('/api/v1/validate', json=raw).status_code == 422
    legacy = client.get('/api/demo').json() | dict(building_type='Apartment', floors=1, selected_measures=[])
    result = client.post('/api/v1/validate', json=legacy)
    assert result.status_code == 200, result.text
    assert result.json()['building_type'] == 'Apartment'
    assert client.post('/api/v1/validate', json=legacy | dict(area_basis='per_floor',entered_area=100)).status_code == 422
