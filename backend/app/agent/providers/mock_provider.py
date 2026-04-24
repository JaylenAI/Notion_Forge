"""Mock AI Provider — API 키 없이 로컬 폴백용"""

import logging
from typing import Any

from app.agent.providers.base import BaseProvider

logger = logging.getLogger("notionforge.providers.mock")


class MockProvider(BaseProvider):
    name = "mock"

    async def call(self, system_prompt: str, user_message: str, model: str = "") -> dict[str, Any] | None:
        logger.info("[MockProvider] AI 키 미설정 — None 반환, 폴백 템플릿 사용")
        return None
