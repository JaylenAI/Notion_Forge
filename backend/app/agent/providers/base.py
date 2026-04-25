"""BaseProvider: AI 프로바이더 추상 클래스 + 재시도 + 지수 백오프"""

import asyncio
import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger("notionforge.providers")

DEFAULT_TIMEOUT_SECONDS = 45
MAX_RETRIES = 2
INITIAL_BACKOFF_SECONDS = 0.5

_TRANSIENT_INDICATORS = ("429", "rate", "503", "502", "500", "overloaded", "capacity", "timeout", "timed out")
_PERMANENT_INDICATORS = ("401", "403", "invalid_api_key", "authentication", "permission")


def _is_transient_error(error: Exception) -> bool:
    msg = str(error).lower()
    if any(ind in msg for ind in _PERMANENT_INDICATORS):
        return False
    return any(ind in msg for ind in _TRANSIENT_INDICATORS) or isinstance(
        error, (asyncio.TimeoutError, ConnectionError)
    )


class BaseProvider(ABC):
    """모든 AI 프로바이더가 구현해야 하는 인터페이스"""

    name: str = "base"
    supports_json_mode: bool = False
    supports_function_calling: bool = False

    @abstractmethod
    async def call(self, system_prompt: str, user_message: str, model: str = "") -> dict[str, Any] | None:
        """AI에게 시스템 프롬프트 + 유저 메시지를 보내고 JSON dict를 반환"""
        ...

    async def call_with_tools(
        self,
        system_prompt: str,
        user_message: str,
        tools: list[dict[str, Any]],
        model: str = "",
    ) -> dict[str, Any] | None:
        """Function calling으로 AI 호출. 기본 구현은 일반 call()로 폴백."""
        return await self.call(system_prompt, user_message, model)

    async def call_with_timeout(
        self,
        system_prompt: str,
        user_message: str,
        model: str = "",
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> dict[str, Any] | None:
        try:
            return await asyncio.wait_for(self.call(system_prompt, user_message, model), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"[{self.name}] API 호출 타임아웃 ({timeout}s)")
            return None

    async def call_with_retry(
        self,
        system_prompt: str,
        user_message: str,
        model: str = "",
        max_retries: int = MAX_RETRIES,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> dict[str, Any] | None:
        """지수 백오프로 재시도하는 API 호출. transient 에러만 재시도."""
        last_error: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                result = await asyncio.wait_for(
                    self.call(system_prompt, user_message, model),
                    timeout=timeout,
                )
                if result is not None:
                    if attempt > 0:
                        logger.info(f"[{self.name}] 재시도 {attempt}회 후 성공")
                    return result
                return None
            except Exception as e:
                last_error = e
                if not _is_transient_error(e) or attempt == max_retries:
                    logger.warning(f"[{self.name}] 호출 실패 (시도 {attempt + 1}/{max_retries + 1}): {str(e)[:150]}")
                    return None
                backoff = INITIAL_BACKOFF_SECONDS * (2**attempt)
                logger.info(f"[{self.name}] transient 에러, {backoff:.1f}s 후 재시도 ({attempt + 1}/{max_retries + 1})")
                await asyncio.sleep(backoff)

        if last_error:
            logger.warning(f"[{self.name}] 최대 재시도 초과: {str(last_error)[:150]}")
        return None

    def get_max_prompt_chars(self) -> int:
        """프로바이더별 프롬프트 최대 길이. 기본값은 무제한."""
        return 0

    @staticmethod
    def extract_json(text: str) -> dict[str, Any] | None:
        """AI 응답에서 JSON 추출 (공통 유틸)"""
        if not text:
            return None

        json_match = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                pass

        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass

        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass

        return None

    @staticmethod
    def extract_blueprint_json(text: str) -> dict[str, Any] | None:
        """Blueprint 전용 JSON 추출 — databases 또는 db_properties 필드 필수"""
        data = BaseProvider.extract_json(text)
        if data and ("databases" in data or "db_properties" in data):
            return data
        return None
