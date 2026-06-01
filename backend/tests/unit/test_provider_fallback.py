"""provider-on-None 폴백 후보 선정 로직 테스트 (TEST-COV-01).

라이브에서 검증한 '1차 None → 건강한 provider로 폴백' 동작의 핵심 로직 회귀 방지.
circuit-open provider 건너뛰기 + copilot(키 불필요) 포함 + 건강순 정렬 포함.
"""

from app.agent.blueprint_generator import _fallback_candidates
from app.agent.providers.router import _circuit_breaker
from app.config import settings


def test_candidates_with_all_keys(monkeypatch):
    monkeypatch.setattr(settings, "copilot_enabled", False, raising=False)
    monkeypatch.setattr(settings, "anthropic_api_key", "a", raising=False)
    monkeypatch.setattr(settings, "gemini_api_key", "g", raising=False)
    monkeypatch.setattr(settings, "groq_api_key", "q", raising=False)
    _circuit_breaker.reset()
    c = _fallback_candidates("copilot")
    names = [n for n, _ in c]
    assert "copilot" not in names  # 키기반 3개 모두 (max 3)
    assert set(names) == {"groq", "gemini", "claude"}


def test_candidates_exclude_primary(monkeypatch):
    monkeypatch.setattr(settings, "copilot_enabled", False, raising=False)
    monkeypatch.setattr(settings, "anthropic_api_key", "a", raising=False)
    monkeypatch.setattr(settings, "gemini_api_key", "g", raising=False)
    monkeypatch.setattr(settings, "groq_api_key", "", raising=False)
    _circuit_breaker.reset()
    names = [n for n, _ in _fallback_candidates("claude")]
    assert "claude" not in names
    assert "gemini" in names


def test_candidates_no_keys_empty(monkeypatch):
    monkeypatch.setattr(settings, "copilot_enabled", False, raising=False)
    monkeypatch.setattr(settings, "anthropic_api_key", "", raising=False)
    monkeypatch.setattr(settings, "gemini_api_key", "", raising=False)
    monkeypatch.setattr(settings, "groq_api_key", "", raising=False)
    _circuit_breaker.reset()
    assert _fallback_candidates("copilot") == []


def test_candidates_only_keyed_providers(monkeypatch):
    monkeypatch.setattr(settings, "copilot_enabled", False, raising=False)
    monkeypatch.setattr(settings, "anthropic_api_key", "", raising=False)
    monkeypatch.setattr(settings, "gemini_api_key", "g", raising=False)
    monkeypatch.setattr(settings, "groq_api_key", "", raising=False)
    _circuit_breaker.reset()
    assert _fallback_candidates("copilot") == [("gemini", "g")]


def test_candidates_include_copilot_when_enabled(monkeypatch):
    """copilot은 키 불필요(구독 인증)이므로 primary가 아니면 폴백 후보에 포함된다."""
    monkeypatch.setattr(settings, "copilot_enabled", True, raising=False)
    monkeypatch.setattr(settings, "anthropic_api_key", "", raising=False)
    monkeypatch.setattr(settings, "gemini_api_key", "g", raising=False)
    monkeypatch.setattr(settings, "groq_api_key", "q", raising=False)
    _circuit_breaker.reset()
    names = [n for n, _ in _fallback_candidates("gemini")]
    assert "copilot" in names
    assert "gemini" not in names  # primary 제외


def test_candidates_skip_circuit_open(monkeypatch):
    """circuit-open provider(예: 429 누적된 gemini)는 폴백 후보에서 제외된다 (라이브 회귀)."""
    monkeypatch.setattr(settings, "copilot_enabled", False, raising=False)
    monkeypatch.setattr(settings, "anthropic_api_key", "", raising=False)
    monkeypatch.setattr(settings, "gemini_api_key", "g", raising=False)
    monkeypatch.setattr(settings, "groq_api_key", "q", raising=False)
    _circuit_breaker.reset()
    for _ in range(3):  # 임계치까지 실패 누적 → gemini 차단
        _circuit_breaker.record_failure("gemini")
    names = [n for n, _ in _fallback_candidates("copilot")]
    assert "gemini" not in names, "circuit-open된 gemini는 건너뛰어야 함"
    assert "groq" in names
    _circuit_breaker.reset()
