import json
from unittest.mock import patch
import httpx
from backend.app.services import ai_fallback as ai

CONTEXT = json.dumps({"evidence": [{"reference": "S1"}]})
TEXT = "Water efficiency is one option worth reviewing with your builder. [S1]"

def reply(text=TEXT):
    return httpx.Response(200, request=httpx.Request("POST", "https://api.groq.com"), json={"choices": [{"finish_reason": "stop", "message": {"content": text}}]})

def keys(monkeypatch):
    for p in ai.PROVIDERS:
        monkeypatch.setenv(p.upper() + "_API_KEY", "test-key")

def test_first_success_does_not_call_backups(monkeypatch):
    keys(monkeypatch)
    with patch.object(ai.gemini, "generate") as gemini, patch.object(ai.httpx, "post", return_value=reply()) as request:
        assert ai.generate("system", CONTEXT) == (TEXT, 1, "complete")
        assert request.call_count == 1
        assert request.call_args.args[0].startswith("https://openrouter.ai/")
        gemini.assert_not_called()
    assert ai.trace()["explanation_provider"] == "openrouter"
    assert ai.trace()["groq"] == "not_requested"
    assert ai.trace()["gemini"] == "not_requested"


def test_second_success_never_calls_third(monkeypatch):
    keys(monkeypatch)
    failure = httpx.Response(429, request=httpx.Request("POST", "https://openrouter.ai"))
    with patch.object(ai.gemini, "generate") as gemini, patch.object(ai.httpx, "post", side_effect=[failure, reply()]) as request:
        assert ai.generate("system", CONTEXT) == (TEXT, 2, "complete")
        assert request.call_count == 2
        assert request.call_args.args[0].startswith("https://api.groq.com/")
        gemini.assert_not_called()
    assert ai.trace()["openrouter"] == "quota_reached"
    assert ai.trace()["gemini"] == "not_requested"
    assert ai.trace()["explanation_provider"] == "groq"


def test_invalid_second_response_reaches_third(monkeypatch):
    keys(monkeypatch)
    with patch.object(ai.gemini, "generate", return_value=(TEXT, 1, "complete")) as gemini, patch.object(ai.httpx, "post", side_effect=[reply("You save $999."), reply("Advice [S99]")]) as request:
        assert ai.generate("system", CONTEXT) == (TEXT, 3, "complete")
        assert request.call_count == 2
        gemini.assert_called_once()
    assert ai.trace()["openrouter"] == "rejected_response"
    assert ai.trace()["groq"] == "rejected_response"
    assert ai.trace()["explanation_provider"] == "gemini"


def test_missing_keys_make_no_requests():
    with patch.object(ai.httpx, "post") as request:
        assert ai.generate("system", CONTEXT)[0] is None
        request.assert_not_called()
    assert ai.trace()["explanation_provider"] == "calculated"

def test_paid_openrouter_model_is_not_called(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "paid/model")
    with patch.object(ai.httpx, "post") as request:
        ai.generate("system", CONTEXT)
        request.assert_not_called()
    assert ai.trace()["openrouter"] == "free_model_required"

def test_invalid_citation_rejected():
    assert not ai.usable("Advice [S99]", CONTEXT)
    assert not ai.usable("You save five dollars.", CONTEXT)
    assert ai.usable(TEXT, CONTEXT)


def test_reasoning_models_leave_budget_for_final_answer(monkeypatch):
    keys(monkeypatch)
    monkeypatch.setenv("GROQ_MODEL", "openai/gpt-oss-20b")
    monkeypatch.setenv("OPENROUTER_MODEL", "openrouter/free")
    with patch.object(ai.httpx, "post", return_value=reply()) as request:
        ai.chat("groq", "system", CONTEXT, 12)
        payload = request.call_args.kwargs["json"]
        assert payload["reasoning_effort"] == "low"
        assert payload["include_reasoning"] is False
        assert payload["max_tokens"] == 4096
        ai.chat("openrouter", "system", CONTEXT, 12)
        assert request.call_args.kwargs["json"]["reasoning"] == {"effort": "low", "exclude": True}


def test_other_groq_models_do_not_receive_unsupported_reasoning_setting(monkeypatch):
    keys(monkeypatch)
    monkeypatch.setenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    with patch.object(ai.httpx, "post", return_value=reply()) as request:
        ai.chat("groq", "system", CONTEXT, 12)
        assert "reasoning_effort" not in request.call_args.kwargs["json"]
        assert "include_reasoning" not in request.call_args.kwargs["json"]


def test_workflow_reports_openrouter_success_without_calling_backups(monkeypatch):
    from fastapi.testclient import TestClient
    from backend.app.main import app
    keys(monkeypatch)
    client = TestClient(app)
    with patch.object(ai.gemini, "generate") as gemini, patch.object(ai.httpx, "post", return_value=reply()) as request:
        result = client.post("/api/analyse", json=client.get("/api/demo").json()).json()
        assert request.call_count == 1
    gemini.assert_not_called()
    assert result["research_status"]["gemini"] == "not_requested"
    assert result["research_status"]["groq"] == "not_requested"
    assert result["research_status"]["openrouter"] == "complete"
    assert result["research_status"]["explanation_provider"] == "openrouter"
    assert result["periods"]["40"]["explanation"][-1] == TEXT


def test_timeout_and_empty_backups_finish_with_calculated_fallback(monkeypatch):
    keys(monkeypatch)
    with patch.object(ai.gemini, "generate", return_value=(None, 1, "unavailable")), patch.object(ai.httpx, "post", side_effect=[httpx.ReadTimeout("timed out"), reply("")]):
        assert ai.generate("system", CONTEXT) == (None, 3, "unavailable")
    assert ai.trace()["explanation_provider"] == "calculated"
    assert ai.trace()["groq"] == "empty_response"
