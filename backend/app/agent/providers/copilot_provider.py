"""GitHub Copilot SDK Provider with Model Escalation"""

import logging
from typing import Any

from app.agent.providers.base import BaseProvider

logger = logging.getLogger("notionforge.providers.copilot")

# Model Escalation 순서: 기본 -> 더 강력한 모델
COPILOT_ESCALATION = ["gpt-4.1", "gpt-5.2", "gpt-5-mini"]


class CopilotProvider(BaseProvider):
    name = "copilot"

    def __init__(self, model: str = ""):
        self.default_model = model or ""

    async def call(self, system_prompt: str, user_message: str, model: str = "") -> dict[str, Any] | None:
        """GitHub Copilot SDK를 통한 AI 호출 -- Model Escalation 포함"""
        try:
            from app.config import settings
            from app.core.copilot_client import copilot_manager

            primary_model = model or self.default_model or settings.copilot_model
            models_to_try = [primary_model]

            # Escalation: 기본 모델이 실패하면 다음 모델 시도
            for m in COPILOT_ESCALATION:
                if m != primary_model and m not in models_to_try:
                    models_to_try.append(m)
            models_to_try = models_to_try[:3]  # 최대 3개 모델

            for i, try_model in enumerate(models_to_try):
                try:
                    text = await copilot_manager.send(
                        system_prompt=system_prompt,
                        user_message=user_message,
                        model=try_model,
                    )
                    if text:
                        result = self.extract_json(text)
                        if result:
                            if i > 0:
                                logger.info(f"[Model Escalation] {primary_model} -> {try_model} 성공")
                            return result
                        logger.info(f"[Copilot {try_model}] JSON 파싱 실패, 다음 모델 시도")
                    else:
                        logger.info(f"[Copilot {try_model}] 빈 응답, 다음 모델 시도")
                except Exception as e:
                    logger.info(f"[Copilot {try_model} 에러] {str(e)[:80]}")

            return None
        except Exception as e:
            logger.warning(f"[Copilot 에러] {e}")
            return None
