"""Phase 5: Provider 안정성 — Retry, Circuit Breaker, Fallback Chain 테스트"""

import asyncio
from unittest.mock import patch

import pytest

from app.agent.providers.base import (
    BaseProvider,
    _is_transient_error,
)
from app.agent.providers.router import CircuitBreaker, ProviderRouter


class FakeProvider(BaseProvider):
    name = "fake"

    def __init__(self):
        self.call_count = 0
        self._responses: list = []

    def set_responses(self, responses: list):
        self._responses = list(responses)

    async def call(self, system_prompt: str, user_message: str, model: str = ""):
        self.call_count += 1
        if self._responses:
            resp = self._responses.pop(0)
            if isinstance(resp, Exception):
                raise resp
            return resp
        return {"result": "ok"}


class TestIsTransientError:
    def test_429_is_transient(self):
        assert _is_transient_error(Exception("429 Too Many Requests"))

    def test_503_is_transient(self):
        assert _is_transient_error(Exception("503 Service Unavailable"))

    def test_rate_limit_is_transient(self):
        assert _is_transient_error(Exception("rate limit exceeded"))

    def test_timeout_is_transient(self):
        assert _is_transient_error(asyncio.TimeoutError())

    def test_connection_error_is_transient(self):
        assert _is_transient_error(ConnectionError("connection refused"))

    def test_401_is_permanent(self):
        assert not _is_transient_error(Exception("401 Unauthorized"))

    def test_403_is_permanent(self):
        assert not _is_transient_error(Exception("403 Forbidden"))

    def test_invalid_api_key_is_permanent(self):
        assert not _is_transient_error(Exception("invalid_api_key"))

    def test_unknown_error_is_not_transient(self):
        assert not _is_transient_error(Exception("some random error"))

    def test_overloaded_is_transient(self):
        assert _is_transient_error(Exception("Model is overloaded"))


class TestCallWithRetry:
    @pytest.mark.asyncio
    async def test_success_on_first_try(self):
        provider = FakeProvider()
        provider.set_responses([{"data": "ok"}])
        result = await provider.call_with_retry("sys", "user", max_retries=2, timeout=5.0)
        assert result == {"data": "ok"}
        assert provider.call_count == 1

    @pytest.mark.asyncio
    async def test_retries_on_transient_error(self):
        provider = FakeProvider()
        provider.set_responses(
            [
                Exception("429 Too Many Requests"),
                {"data": "ok"},
            ]
        )
        result = await provider.call_with_retry("sys", "user", max_retries=2, timeout=5.0)
        assert result == {"data": "ok"}
        assert provider.call_count == 2

    @pytest.mark.asyncio
    async def test_no_retry_on_permanent_error(self):
        provider = FakeProvider()
        provider.set_responses([Exception("401 Unauthorized")])
        result = await provider.call_with_retry("sys", "user", max_retries=2, timeout=5.0)
        assert result is None
        assert provider.call_count == 1

    @pytest.mark.asyncio
    async def test_exhausted_retries(self):
        provider = FakeProvider()
        provider.set_responses(
            [
                Exception("429 rate limit"),
                Exception("429 rate limit"),
                Exception("429 rate limit"),
            ]
        )
        result = await provider.call_with_retry("sys", "user", max_retries=2, timeout=5.0)
        assert result is None
        assert provider.call_count == 3

    @pytest.mark.asyncio
    async def test_returns_none_when_call_returns_none(self):
        provider = FakeProvider()
        provider.set_responses([None])
        result = await provider.call_with_retry("sys", "user", max_retries=2, timeout=5.0)
        assert result is None
        assert provider.call_count == 1


class TestCircuitBreaker:
    def test_initially_closed(self):
        cb = CircuitBreaker(threshold=3)
        assert not cb.is_open("openai")

    def test_opens_after_threshold(self):
        cb = CircuitBreaker(threshold=3)
        cb.record_failure("openai")
        cb.record_failure("openai")
        assert not cb.is_open("openai")
        cb.record_failure("openai")
        assert cb.is_open("openai")

    def test_resets_on_success(self):
        cb = CircuitBreaker(threshold=2)
        cb.record_failure("openai")
        cb.record_failure("openai")
        assert cb.is_open("openai")
        cb.record_success("openai")
        assert not cb.is_open("openai")

    def test_auto_reset_after_timeout(self):
        cb = CircuitBreaker(threshold=2, reset_seconds=0.01)
        cb.record_failure("claude")
        cb.record_failure("claude")
        assert cb.is_open("claude")
        import time

        time.sleep(0.02)
        assert not cb.is_open("claude")

    def test_status_report(self):
        cb = CircuitBreaker(threshold=3)
        cb.record_failure("openai")
        cb.record_failure("openai")
        status = cb.get_status()
        assert "openai" in status
        assert status["openai"]["failures"] == 2
        assert status["openai"]["open"] is False

    def test_reset_clears_all(self):
        cb = CircuitBreaker(threshold=2)
        cb.record_failure("openai")
        cb.record_failure("openai")
        cb.reset()
        assert not cb.is_open("openai")

    def test_independent_providers(self):
        cb = CircuitBreaker(threshold=2)
        cb.record_failure("openai")
        cb.record_failure("openai")
        assert cb.is_open("openai")
        assert not cb.is_open("claude")


class TestProviderFallback:
    def test_resolve_with_fallback_uses_primary(self):
        ProviderRouter.circuit_breaker.reset()
        with patch("app.agent.providers.router.create_provider") as mock_create:
            mock_create.return_value = FakeProvider()
            ProviderRouter.resolve_with_fallback(api_key="sk-test123")
            mock_create.assert_called_once_with("openai", api_key="sk-test123", model="")

    def test_resolve_with_fallback_skips_open_circuit(self, monkeypatch):
        from app.config import settings

        # fallback이 선택 가능하도록 copilot(키 불필요) 활성화 (conftest가 기본 비활성)
        monkeypatch.setattr(settings, "copilot_enabled", True, raising=False)
        ProviderRouter.circuit_breaker.reset()
        for _ in range(3):
            ProviderRouter.circuit_breaker.record_failure("openai")

        with patch("app.agent.providers.router.create_provider") as mock_create:
            mock_create.return_value = FakeProvider()
            ProviderRouter.resolve_with_fallback(api_key="sk-test123")
            call_args = mock_create.call_args
            assert call_args[0][0] != "openai"

        ProviderRouter.circuit_breaker.reset()

    def test_resolve_with_fallback_resets_when_all_open(self):
        ProviderRouter.circuit_breaker.reset()
        # copilot 포함 전 프로바이더가 모두 차단된 경우에만 reset → primary 강제
        for name in ["copilot", "openai", "claude", "gemini", "groq"]:
            for _ in range(3):
                ProviderRouter.circuit_breaker.record_failure(name)

        with patch("app.agent.providers.router.create_provider") as mock_create:
            mock_create.return_value = FakeProvider()
            ProviderRouter.resolve_with_fallback(api_key="sk-test123")
            mock_create.assert_called_once_with("openai", api_key="sk-test123", model="")

        ProviderRouter.circuit_breaker.reset()

    def test_basic_resolve_unchanged(self):
        with patch("app.agent.providers.router.create_provider") as mock_create:
            mock_create.return_value = FakeProvider()
            ProviderRouter.resolve(api_key="sk-test123")
            mock_create.assert_called_once_with("openai", api_key="sk-test123", model="")
