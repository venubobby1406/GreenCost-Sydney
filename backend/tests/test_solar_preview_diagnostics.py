from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def project(**changes):
    return client.get('/api/demo').json() | dict(area=250,area_unit='m²',floors=1,
        selected_measures=['solar_pv'],quantity_overrides={},solar_kw=6.6) | changes


def test_250_square_metre_house_accepts_default_solar():
    response=client.post('/api/v1/preview',json=project())
    assert response.status_code==200, response.text
    assert response.json()['takeoff']['quantities']['max_solar_kw']==13.2


def test_small_roof_override_returns_correctable_diagnostics_and_clears_after_change():
    payload=project(quantity_overrides={'roof_area_m2':.5})
    for _ in range(2):  # Retry cannot change the physical input.
        response=client.post('/api/v1/preview',json=payload)
        assert response.status_code==422
        detail=response.json()['detail']
        assert detail['code']=='solar_capacity'
        q=detail['geometry']
        assert q['area']==250 and q['area_unit']=='m²' and q['floors']==1
        assert q['roof_overridden'] is True and q['roof_area_m2']==.5
        assert q['max_solar_kw']==.04 and q['solar_kw']==6.6
    assert client.post('/api/v1/preview',json=payload|dict(quantity_overrides={})).status_code==200
    # Calculation continues enforcing the same bound, not only the preview.
    assert client.post('/api/analyse',json=payload).status_code==422


def test_unit_and_floor_diagnostics_explain_a_low_limit():
    response=client.post('/api/v1/preview',json=project(area_unit='ft²',floors=50))
    assert response.status_code==422
    q=response.json()['detail']['geometry']
    assert q['area_m2']==250*.092903 and q['floors']==50
    assert .04<q['max_solar_kw']<.05 and q['roof_overridden'] is False
