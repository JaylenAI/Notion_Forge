import os

import pytest


@pytest.fixture(autouse=True)
def _force_mock_provider(monkeypatch):
    """테스트는 기본적으로 실제 LLM provider를 호출하지 않는다.

    copilot 비활성 + AI 키 제거 → settings.ai_provider == "mock" 이 되어
    resolve()/resolve_with_fallback()가 MockProvider를 반환한다.
    이로써 패치가 누락된 경로(예: 모듈 내부로 import된 generate_blueprint 참조)에서도
    실제 네트워크/구독 호출이 발생하지 않는다.

    실제 provider를 검증해야 하는 테스트는 provider 인스턴스를 직접 생성(api_key 전달)한다.
    """
    from app.config import settings

    monkeypatch.setattr(settings, "copilot_enabled", False, raising=False)
    monkeypatch.setattr(settings, "anthropic_api_key", "", raising=False)
    monkeypatch.setattr(settings, "gemini_api_key", "", raising=False)
    monkeypatch.setattr(settings, "groq_api_key", "", raising=False)
    # Notion 키도 비워 테스트가 실수로 실제 Notion API를 치지 않게 함 (TEST-ISO-01)
    monkeypatch.setattr(settings, "notion_api_key", "", raising=False)
    monkeypatch.setattr(settings, "notion_parent_page_id", "", raising=False)
    monkeypatch.setenv("COPILOT_ENABLED", "false")
    for k in ("ANTHROPIC_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY", "NOTION_API_KEY", "NOTION_PARENT_PAGE_ID"):
        monkeypatch.delenv(k, raising=False)
    os.environ.setdefault("NOTIONFORGE_TEST", "1")

    # WebSocket 연결 rate limit 상태는 모듈 전역이라 테스트 간 누적 방지를 위해 리셋
    try:
        from app.routers import chat as _chat

        _chat._ws_active.clear()
        _chat._ws_recent_connects.clear()
    except Exception:
        pass

    # LLM 호출 예산(ContextVar) 테스트 간 격리
    try:
        from app.core.cost_control import reset_budget

        reset_budget()
    except Exception:
        pass

    # Circuit Breaker 싱글톤 테스트 간 리셋 (TEST-ISO-02)
    try:
        from app.agent.providers.router import _circuit_breaker

        _circuit_breaker.reset()
    except Exception:
        pass


@pytest.fixture
def sample_prompt():
    return "프로젝트 관리 대시보드 만들어줘, 주황색으로"
