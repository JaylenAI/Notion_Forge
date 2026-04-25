"""Gemini AI Provider — JSON mode + system_instruction 지원"""

import logging
from typing import Any

from app.agent.providers.base import BaseProvider

logger = logging.getLogger("notionforge.providers.gemini")


class GeminiProvider(BaseProvider):
    name = "gemini"
    supports_json_mode = True
    supports_function_calling = True

    def __init__(self, api_key: str = "", model: str = ""):
        self.api_key = api_key
        self.default_model = model or "gemini-2.5-flash"

    async def call(self, system_prompt: str, user_message: str, model: str = "") -> dict[str, Any] | None:
        try:
            from google import genai
            from google.genai import types

            from app.config import settings

            client = genai.Client(api_key=self.api_key or settings.gemini_api_key)
            response = await client.aio.models.generate_content(
                model=model or self.default_model,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    temperature=0.3,
                ),
            )
            text = response.text or ""
            if not text:
                logger.warning("[Gemini] 빈 응답 반환")
                return None

            result = self.extract_json(text)
            if result is None:
                logger.warning(f"[Gemini] JSON 파싱 실패: {text[:200]}")
            return result
        except ImportError:
            logger.warning("[Gemini] google-genai 패키지 미설치")
            return None
        except Exception as e:
            logger.warning(f"[Gemini 에러] {type(e).__name__}: {str(e)[:150]}")
            return None

    async def call_with_tools(
        self,
        system_prompt: str,
        user_message: str,
        tools: list[dict[str, Any]],
        model: str = "",
    ) -> dict[str, Any] | None:
        try:
            from google import genai
            from google.genai import types

            from app.config import settings

            function_declarations = []
            for t in tools:
                func = t.get("function", {})
                function_declarations.append(
                    types.FunctionDeclaration(
                        name=func["name"],
                        description=func.get("description", ""),
                        parameters=func.get("parameters", {}),
                    )
                )

            gemini_tools = [types.Tool(function_declarations=function_declarations)]

            client = genai.Client(api_key=self.api_key or settings.gemini_api_key)
            response = await client.aio.models.generate_content(
                model=model or self.default_model,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    tools=gemini_tools,
                    temperature=0.3,
                ),
            )

            tool_calls = []
            text_content = ""
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    tool_calls.append(
                        {
                            "name": part.function_call.name,
                            "arguments": dict(part.function_call.args) if part.function_call.args else {},
                        }
                    )
                elif part.text:
                    text_content = part.text

            if tool_calls:
                return {"tool_calls": tool_calls}
            return self.extract_json(text_content)
        except ImportError:
            logger.warning("[Gemini] google-genai 패키지 미설치")
            return None
        except Exception as e:
            logger.warning(f"[Gemini FC 에러] {type(e).__name__}: {str(e)[:150]}")
            return None
