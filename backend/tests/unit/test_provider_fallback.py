"""provider-on-None 폴백 후보 선정 로직 테스트 (TEST-COV-01).

라이브에서 검증한 '1차 None → 키 있는 provider로 폴백' 동작의 핵심 로직 회귀 방지.
"""

from app.agent.blueprint_generator import _fallback_candidates
from app.config import settings


def test_candidates_with_all_keys_capped_at_two(monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", "a", raising=False)
    monkeypatch.setattr(settings, "gemini_api_key", "g", raising=False)
    monkeypatch.setattr(settings, "groq_api_key", "q", raising=False)
    c = _fallback_candidates("copilot")
    assert len(c) == 2, "최대 2개로 제한돼야 함"
    assert "copilot" not in [n for n, _ in c]


def test_candidates_exclude_primary(monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", "a", raising=False)
    monkeypatch.setattr(settings, "gemini_api_key", "g", raising=False)
    monkeypatch.setattr(settings, "groq_api_key", "", raising=False)
    names = [n for n, _ in _fallback_candidates("claude")]
    assert "claude" not in names
    assert "gemini" in names


def test_candidates_no_keys_empty(monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", "", raising=False)
    monkeypatch.setattr(settings, "gemini_api_key", "", raising=False)
    monkeypatch.setattr(settings, "groq_api_key", "", raising=False)
    assert _fallback_candidates("copilot") == []


def test_candidates_only_keyed_providers(monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", "", raising=False)
    monkeypatch.setattr(settings, "gemini_api_key", "g", raising=False)
    monkeypatch.setattr(settings, "groq_api_key", "", raising=False)
    c = _fallback_candidates("copilot")
    assert c == [("gemini", "g")]
