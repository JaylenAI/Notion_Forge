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
    monkeypatch.setenv("COPILOT_ENABLED", "false")
    for k in ("ANTHROPIC_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY"):
        monkeypatch.delenv(k, raising=False)
    os.environ.setdefault("NOTIONFORGE_TEST", "1")


@pytest.fixture
def sample_prompt():
    return "프로젝트 관리 대시보드 만들어줘, 주황색으로"
