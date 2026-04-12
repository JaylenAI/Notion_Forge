"""BaseProvider: AI 프로바이더 추상 클래스"""

import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger("notionforge.providers")


class BaseProvider(ABC):
    """모든 AI 프로바이더가 구현해야 하는 인터페이스"""

    name: str = "base"

    @abstractmethod
    async def call(self, system_prompt: str, user_message: str, model: str = "") -> dict[str, Any] | None:
        """AI에게 시스템 프롬프트 + 유저 메시지를 보내고 JSON dict를 반환"""
        ...

    @staticmethod
    def extract_json(text: str) -> dict[str, Any] | None:
        """AI 응답에서 JSON 추출 (공통 유틸)"""
        if not text:
            return None

        # 1. ```json ... ``` 블록
        json_match = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # 2. 전체가 JSON
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass

        # 3. 첫 번째 { ... 마지막 } 추출
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass

        return None
