"""ProviderRouter: API 키 기반 프로바이더 자동 선택 + Circuit Breaker + Fallback Chain"""

import logging
import time
from typing import Any

from app.agent.providers.base import BaseProvider

logger = logging.getLogger("notionforge.provider_router")

CIRCUIT_BREAKER_THRESHOLD = 3
CIRCUIT_BREAKER_RESET_SECONDS = 120.0

# copilot 우선 (키 불필요, GitHub 구독 인증) → 키 기반 프로바이더 순.
# primary는 fallback 시 제외되므로 전 프로바이더를 나열한다.
_FALLBACK_ORDER = ["copilot", "claude", "gemini", "groq", "openai"]


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


class CircuitBreaker:
    """프로바이더별 연속 실패 추적 — 임계치 초과 시 자동 차단"""

    def __init__(
        self,
        threshold: int = CIRCUIT_BREAKER_THRESHOLD,
        reset_seconds: float = CIRCUIT_BREAKER_RESET_SECONDS,
    ):
        self._threshold = threshold
        self._reset_seconds = reset_seconds
        self._failures: dict[str, int] = {}
        self._last_failure_time: dict[str, float] = {}

    def record_success(self, provider_name: str) -> None:
        self._failures[provider_name] = 0

    def record_failure(self, provider_name: str) -> None:
        self._failures[provider_name] = self._failures.get(provider_name, 0) + 1
        self._last_failure_time[provider_name] = time.monotonic()
        logger.info(f"[CircuitBreaker] {provider_name} 실패 {self._failures[provider_name]}/{self._threshold}")

    def is_open(self, provider_name: str) -> bool:
        failures = self._failures.get(provider_name, 0)
        if failures < self._threshold:
            return False
        last_time = self._last_failure_time.get(provider_name, 0)
        if time.monotonic() - last_time > self._reset_seconds:
            self._failures[provider_name] = 0
            logger.info(f"[CircuitBreaker] {provider_name} 리셋 (half-open)")
            return False
        return True

    def get_status(self) -> dict[str, Any]:
        return {
            name: {"failures": self._failures.get(name, 0), "open": self.is_open(name)}
            for name in set(list(self._failures.keys()))
        }

    def reset(self) -> None:
        self._failures.clear()
        self._last_failure_time.clear()


_circuit_breaker = CircuitBreaker()


class ProviderRouter:
    """AI 프로바이더 자동 라우팅 + Circuit Breaker + Fallback Chain"""

    circuit_breaker = _circuit_breaker

    @staticmethod
    def resolve(api_key: str = "", ai_model: str = "") -> BaseProvider:
        """API 키 또는 설정 기반으로 최적 프로바이더 반환"""
        if api_key:
            provider_name = detect_provider_from_key(api_key)
            return create_provider(provider_name, api_key=api_key, model=ai_model)

        from app.config import settings

        provider_name = settings.ai_provider
        return create_provider(provider_name, model=ai_model)

    @staticmethod
    def _settings_key_for(provider_name: str) -> str:
        """fallback 프로바이더가 사용할 settings API 키. copilot/openai는 settings 키가 없다."""
        from app.config import settings

        return {
            "claude": settings.anthropic_api_key,
            "gemini": settings.gemini_api_key,
            "groq": settings.groq_api_key,
        }.get(provider_name, "")

    @staticmethod
    def resolve_with_fallback(api_key: str = "", ai_model: str = "") -> BaseProvider:
        """Circuit Breaker를 확인하여 건강한 프로바이더 반환.
        primary가 차단되면 fallback chain에서 '키가 있거나 키가 불필요한' 대체 프로바이더 선택."""
        from app.config import settings

        if api_key:
            primary = detect_provider_from_key(api_key)
        else:
            primary = settings.ai_provider

        if not _circuit_breaker.is_open(primary):
            return create_provider(primary, api_key=api_key, model=ai_model)

        logger.warning(f"[ProviderRouter] {primary} circuit open, fallback 탐색")
        for fallback_name in _FALLBACK_ORDER:
            if fallback_name == primary or _circuit_breaker.is_open(fallback_name):
                continue
            # copilot은 키 불필요(구독 인증), 나머지는 settings 키가 있어야 의미 있음
            if fallback_name == "copilot":
                if not settings.copilot_enabled:
                    continue
                fb_key = ""
            else:
                fb_key = ProviderRouter._settings_key_for(fallback_name)
                if not fb_key:
                    continue
            logger.info(f"[ProviderRouter] fallback → {fallback_name}")
            return create_provider(fallback_name, api_key=fb_key, model=ai_model)

        logger.warning("[ProviderRouter] 모든 프로바이더 차단/키없음, primary 강제 사용")
        _circuit_breaker.reset()
        return create_provider(primary, api_key=api_key, model=ai_model)
