import io
from unittest.mock import patch
from fastapi.testclient import TestClient
from pypdf import PdfReader
from backend.app.main import app
from backend.app.services.pdf_report import pdf_report

client = TestClient(app)
TEXT = "Insulation helps keep the home comfortable. Confirm the installed quote with your builder. [S1]"


def snapshot():
    result = client.post("/api/analyse",json=client.get("/api/demo").json()).json()
    return result, dict(project=result["project"],rates=result["rates"],years=40)


def commentary():
    return dict(years=40,provider="openrouter",paragraphs=[TEXT],evidence=[dict(source="Project guide",page=1,source_type="PROJECT_RESEARCH",text="Building comfort guidance")],statuses=dict(openrouter="complete",groq="not_requested",gemini="not_requested"))


def test_export_explains_project_without_provider_metadata_or_external_calls():
    result, data = snapshot()
    with patch("httpx.post",side_effect=AssertionError("Export must not call AI")):
        response=client.post("/api/report/pdf",json=data|dict(commentary=commentary()))
        assert response.status_code==200,response.text[:200]
        reader=PdfReader(io.BytesIO(response.content))
        text="\n".join(page.extract_text() for page in reader.pages)
        assert "Your project explained" in text
        assert "Saved AI commentary" not in text
        assert "Reply received" not in text and "Not called" not in text
        assert "OpenRouter" not in text and "Python" not in text
        assert "compares the conventional and sustainable designs" in " ".join(text.split())
        assert "TOTAL cost over 40 years" in text
        assert "How total costs build over time" not in reader.pages[0].extract_text()
        assert "Project: " + result["project"]["name"] in text
        assert result["project"]["name"] in reader.metadata.title
        assert "Routine maintenance costs are the same" in text
        assert "Complete input record" not in text
        assert 'quantity overrides' not in text
        assert len(reader.pages)==5
        from backend.app.services.explanation import money
        assert money(result["periods"]["40"]["sustainable"]["total_lcc"]) in text
        html=client.post("/api/report",json=data|dict(commentary=commentary())).text
        assert "Your project explained" in html and "Saved AI commentary" not in html
        assert "<pre>" not in html


def test_invalid_or_other_period_commentary_is_not_presented_as_ai():
    _,data=snapshot()
    for edits in (dict(paragraphs=["Guaranteed savings of $999."]),dict(paragraphs=["Unsupported reference [S99]"]),dict(years=30)):
        payload=commentary()|edits
        response=client.post("/api/report/pdf",json=data|dict(commentary=payload))
        text="\n".join(page.extract_text() for page in PdfReader(io.BytesIO(response.content)).pages)
        assert "Saved AI commentary" not in text
        assert "Your project explained" in text
        assert "$999" not in text and "[S99]" not in text
    assert client.post("/api/report/pdf",json=data|dict(commentary=commentary(),totals={"sustainable":1})).status_code==422


def test_report_handles_costlier_design_zero_difference_and_zero_capital():
    result,_=snapshot()
    r=result["periods"]["40"]
    r["savings_aud"]=-1000;r["break_even_year"]=None
    text="".join(p.extract_text() for p in PdfReader(io.BytesIO(pdf_report(result,40))).pages)
    assert "costs AUD $1,000 more" in text
    assert "does not become cheaper" in text
    r["savings_aud"]=0;r["savings_percent"]=None;r["break_even_year"]=0;r["capital_difference"]=0
    text="".join(p.extract_text() for p in PdfReader(io.BytesIO(pdf_report(result,40))).pages)
    assert "same modelled total cost" in text
    assert "year 0" in text


def test_report_html_escapes_commentary_and_reference_names():
    _,data=snapshot()
    captured=commentary()
    captured["paragraphs"]=["Check <script>alert('unsafe')</script> with your builder. [S1]"]
    captured["evidence"][0]["source"]="<img src=x onerror=alert('unsafe')>"
    response=client.post("/api/report",json=data|dict(commentary=captured))
    assert response.status_code==200
    assert "<script>" not in response.text
    assert "<img src=x" not in response.text
    assert "alert('unsafe')" not in response.text


def test_report_replaces_metadata_reply_with_actual_project_and_names_download():
    _,data=snapshot()
    data["project"]["name"]="Courtyard House"
    captured=commentary() | dict(paragraphs=["User Safety: safe"])
    response=client.post("/api/report/pdf",json=data|dict(commentary=captured))
    assert response.status_code==200
    assert 'filename="Courtyard-House-40-year-report.pdf"' in response.headers["content-disposition"]
    reader=PdfReader(io.BytesIO(response.content))
    text="\n".join(page.extract_text() for page in reader.pages)
    assert "User Safety" not in text
    assert "Courtyard House is a house" in text
    assert "Rooftop solar" in text and "6.6 kW" in text
    assert len(reader.pages)==5
    assert "Courtyard House" in reader.metadata.title


def test_report_names_handle_unicode_empty_and_unsafe_characters():
    from backend.app.services.report_names import attachment_header,report_filename
    assert report_filename("  ",40,"pdf")=="GreenCost-40-year-report.pdf"
    assert report_filename('../House: "A"\r\n',40,"pdf")=="House-A-40-year-report.pdf"
    header=attachment_header("Maison été",40,"pdf")
    assert "filename*=UTF-8''Maison-%C3%A9t%C3%A9-40-year-report.pdf" in header
