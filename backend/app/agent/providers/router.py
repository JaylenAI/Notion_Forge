"""ProviderRouter: API 키 기반 프로바이더 자동 선택"""

import logging

from app.agent.providers.base import BaseProvider

logger = logging.getLogger("notionforge.provider_router")


def detect_provider_from_key(api_key: str) -> str:
    """API 키 패턴으로 프로바이더 자동 감지"""
    if not api_key:
        return ""
    if api_key.startswith("sk-ant-"):
        return "claude"
    if api_key.startswith("sk-"):
        return "openai"
    if api_key.startswith("AI") and len(api_key) > 30:
        return "gemini"
    if api_key.startswith("gsk_"):
        return "groq"
    return "openai"


def create_provider(provider_name: str, api_key: str = "", model: str = "") -> BaseProvider:
    """프로바이더 이름으로 인스턴스 생성"""
    # 순환 임포트 방지를 위해 여기서 임포트
    if provider_name == "claude":
        from app.agent.providers.claude_provider import ClaudeProvider

        return ClaudeProvider(api_key=api_key, model=model)
    elif provider_name == "gemini":
        from app.agent.providers.gemini_provider import GeminiProvider

        return GeminiProvider(api_key=api_key, model=model)
    elif provider_name == "groq":
        from app.agent.providers.groq_provider import GroqProvider

        return GroqProvider(api_key=api_key, model=model)
    elif provider_name == "openai":
        from app.agent.providers.openai_provider import OpenAIProvider

        return OpenAIProvider(api_key=api_key, model=model)
    elif provider_name == "copilot":
        from app.agent.providers.copilot_provider import CopilotProvider

        return CopilotProvider(model=model)
    elif provider_name == "mock":
        from app.agent.providers.mock_provider import MockProvider

        return MockProvider()
    else:
        raise ValueError(f"Unknown provider: {provider_name}")


class ProviderRouter:
    """AI 프로바이더 자동 라우팅"""

    @staticmethod
    def resolve(api_key: str = "", ai_model: str = "") -> BaseProvider:
        """API 키 또는 설정 기반으로 최적 프로바이더 반환"""
        if api_key:
            provider_name = detect_provider_from_key(api_key)
            return create_provider(provider_name, api_key=api_key, model=ai_model)

        from app.config import settings

        provider_name = settings.ai_provider
        return create_provider(provider_name, model=ai_model)
