from unittest.mock import patch
import httpx
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services import supplier_prices
from backend.app.services.supplier_prices import price_from_page, allowed_url

client = TestClient(app)


def test_budget_plan_reconciles_and_marks_assumptions():
    r = client.post('/api/v1/cost-plan', json=dict(area=220, floors=1, bathrooms=2, budget_low=600000, budget_high=800000))
    assert r.status_code == 200
    plan = r.json()
    assert plan['midpoint'] == 700000
    assert sum(row['quantity'] * row['unit_cost'] for row in plan['rows']) + plan['other_construction'] == pytest.approx(700000, abs=.001)
    assert all(row['status'] == 'Estimate' for row in plan['rows'])
    assert 'placeholder' not in plan['assumptions'] or 'quote' in plan['assumptions']
    assert 'structural adequacy' in plan['assumptions']
    assert client.post('/api/v1/cost-plan', json=dict(area=220, floors=1, bathrooms=2, budget_low=800000, budget_high=600000)).status_code == 422


def test_budget_range_each_case_recalculates_not_just_rescales():
    sample = client.get('/api/demo').json() | dict(conventional_cost=700000, budget_range=[600000,800000])
    actual = client.post('/api/analyse', json=sample).json()
    for label, cost in [('Low',600000),('Midpoint',700000),('High',800000)]:
        expected = client.post('/api/analyse', json=sample | dict(conventional_cost=cost,budget_range=None)).json()
        for horizon in ['30','40','50']:
            row = actual['budget_scenarios'][label][horizon]
            assert row['conventional'] == pytest.approx(expected['periods'][horizon]['conventional']['total_lcc'])
            assert row['savings_aud'] == pytest.approx(expected['periods'][horizon]['savings_aud'])
    assert client.post('/api/analyse', json=sample | dict(conventional_cost=600000)).status_code == 422


def test_draft_can_restore_missing_numbers_but_not_unknown_fields():
    sample = client.get('/api/demo').json() | dict(area=None,occupants=None,energy_kwh=None,premium=None,water_reduction=None,postcode='',zone='')
    assert client.post('/api/v1/draft',json=sample).status_code == 200
    material = dict(name='Concrete',quantity=None,unit='m³',unit_cost=None,maintenance=None)
    restored = client.post('/api/v1/draft',json=sample | dict(materials=[material]))
    assert restored.status_code == 200
    assert restored.json()['materials'][0]['unit_cost'] is None
    assert client.post('/api/analyse',json=sample).status_code == 422
    assert client.post('/api/v1/draft',json={'api_key':'secret'}).status_code == 422
    assert client.post('/api/v1/draft',json={'selected_measures':None}).status_code == 422


def test_price_extraction_refuses_ambiguous_units_and_missing_gst():
    assert price_from_page('Wall insulation $12.50 per m2 inc GST', 'm²') == 12.5
    for text in ['From $12.50 per m2 inc GST','$12.50 per pack inc GST','$12.50 per m2','$12.50 per m2 inc GST and $15.50 per m2 inc GST','Installed price $12.50 per m2 inc GST']:
        assert price_from_page(text,'m²') is None
    assert not allowed_url('https://bunnings.com.au.evil.example/p', ['bunnings.com.au'])
    assert not allowed_url('http://bunnings.com.au/p', ['bunnings.com.au'])
    assert not allowed_url('https://user:pass@bunnings.com.au/p', ['bunnings.com.au'])


def test_supplier_uses_page_content_and_cache_never_snippets(monkeypatch,tmp_path):
    monkeypatch.setenv('TAVILY_API_KEY','test')
    monkeypatch.setattr(supplier_prices,'DATA',tmp_path)
    monkeypatch.setattr(supplier_prices,'_memory',{})
    monkeypatch.setattr(supplier_prices,'_attempts',{})
    response=httpx.Response(200,json={'results':[{'title':'Wall insulation','url':'https://pricewiseinsulation.com.au/product/wall/','content':'$1 per m2 inc GST','raw_content':'Wall insulation $12.50 per m2 inc GST'}]},request=httpx.Request('POST','https://api.tavily.com/search'))
    with patch('httpx.post',return_value=response) as call:
        r=client.post('/api/v1/supplier-price',json={'item':'insulation'}).json()
        assert r['candidates'][0]['unit_price'] == 12.5
        again=client.post('/api/v1/supplier-price',json={'item':'insulation'}).json()
        assert again['cached'] is True
        assert call.call_count == 1
        assert call.call_args.kwargs['json']['include_raw_content'] == 'text'
    assert 'raw_content' not in next(tmp_path.glob('prices/supplier_*.json')).read_text()


def test_failed_supplier_search_does_not_modify_inputs(monkeypatch):
    monkeypatch.setattr(supplier_prices,'_attempts',{})
    assert client.post('/api/v1/supplier-price',json={'item':'roofing'}).json()['status'] == 'not_configured'
    assert client.post('/api/v1/supplier-price',json={'item':'unknown'}).status_code == 422
    assert client.post('/api/knowledge/pdf',content=b'%PDF').status_code == 404


def test_paired_quotes_use_only_difference_and_allow_cheaper_upgrade():
    sample=client.get('/api/demo').json() | dict(selected_measures=['insulation'], installed_quotes={'insulation':{'baseline':5000,'upgrade':4000}})
    r=client.post('/api/analyse',json=sample)
    assert r.status_code == 200
    result=r.json()
    assert result['measures'][0]['premium'] == -1000
    assert result['periods']['40']['capital_difference'] == -1000
    assert result['periods']['40']['conventional']['components']['capital'] == sample['conventional_cost']
    assert client.post('/api/analyse',json=sample | dict(installed_quotes={'insulation':{'baseline':5000}})).status_code == 422


def test_reference_rate_preview_matches_calculation_engine():
    from backend.app.schemas.models import Project
    from backend.app.research.sources import tariffs
    sample=client.get('/api/demo').json()
    for zone in ['Ausgrid','Endeavour Energy','Essential Energy']:
        for stormwater in [False,True]:
            inputs=dict(zone=zone,building_type='Apartment',price_date='2026-10-06',water_connected=True,wastewater_connected=True,stormwater=stormwater,drought_tariff=False)
            actual=client.post('/api/v1/reference-rates',json=inputs)
            assert actual.status_code == 200
            expected=tariffs(Project.model_validate(sample | inputs | {"selected_measures": []}))
            assert actual.json()['rates'] == expected
    assert client.post('/api/v1/reference-rates',json=dict(zone='unknown')).status_code == 422
    assert client.post('/api/v1/reference-rates',json=dict(zone='Ausgrid',building_type='Commercial / Other')).status_code == 422
    assert client.post('/api/v1/reference-rates',json=dict(zone='Ausgrid',price_date='2030-01-01')).status_code == 422
