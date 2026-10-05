"""Tests never use the owner's credentials or consume real provider quotas."""
import pytest


@pytest.fixture(autouse=True)
def isolated_runtime(tmp_path, monkeypatch):
    from backend.app.services import storage, budget
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("TAVILY_API_KEY", "")
    monkeypatch.setenv("SAVE_LOCAL_ANALYSES", "true")
    monkeypatch.setenv("REQUESTS_PER_MINUTE", "120")
    monkeypatch.delenv("VERCEL", raising=False)
    from backend.app.services import security
    monkeypatch.setattr(security, "_requests", {})
    monkeypatch.setenv("GEMINI_DAILY_CAP", "500")
    monkeypatch.setenv("TAVILY_DAILY_CAP", "500")
    monkeypatch.setenv("GEMINI_MONTHLY_CAP", "5000")
    monkeypatch.setenv("TAVILY_MONTHLY_CAP", "5000")
    monkeypatch.setattr(storage, "DATA", tmp_path)
    monkeypatch.setattr(budget, "DATA", tmp_path)
    monkeypatch.setattr(budget, "_memory", {})
