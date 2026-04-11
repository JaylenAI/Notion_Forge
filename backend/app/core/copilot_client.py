"""GitHub Copilot SDK 싱글턴 래퍼

Copilot SDK를 통해 GPT-4.1, GPT-5.x, Claude 등 다양한 모델에
API 키 없이 접근 가능. GitHub Copilot 구독 인증 기반.
"""

import asyncio
from typing import Any


# 사용 가능한 모델 목록 (런타임에 동적 확인 가능)
COPILOT_MODELS: list[dict[str, str]] = [
    {"id": "gpt-4.1", "name": "GPT-4.1", "provider": "OpenAI", "tier": "recommended"},
    {"id": "gpt-5.2", "name": "GPT-5.2", "provider": "OpenAI", "tier": "premium"},
    {"id": "gpt-5-mini", "name": "GPT-5 Mini", "provider": "OpenAI", "tier": "fast"},
    {"id": "gpt-5.4-mini", "name": "GPT-5.4 Mini", "provider": "OpenAI", "tier": "fast"},
    {"id": "gpt-5.2-codex", "name": "GPT-5.2 Codex", "provider": "OpenAI", "tier": "code"},
    {"id": "gpt-5.3-codex", "name": "GPT-5.3 Codex", "provider": "OpenAI", "tier": "code"},
    {"id": "claude-haiku-4.5", "name": "Claude Haiku 4.5", "provider": "Anthropic", "tier": "fast"},
]


class CopilotManager:
    """GitHub Copilot SDK 싱글턴 관리자

    앱 시작 시 start(), 종료 시 stop() 호출.
    각 AI 호출은 send()로 세션 생성 → 응답 → 반환.
    """

    def __init__(self):
        self._client: Any = None
        self._available: bool | None = None
        self._started = False

    def is_available(self) -> bool:
        """Copilot SDK 사용 가능 여부 (import 가능 + CLI 번들 존재)"""
        if self._available is not None:
            return self._available
        try:
            from copilot import CopilotClient  # noqa: F401
            self._available = True
        except ImportError:
            self._available = False
        return self._available

    async def start(self):
        """CopilotClient 초기화 (앱 시작 시 1회)"""
        if not self.is_available():
            print("[Copilot] SDK를 찾을 수 없습니다. Copilot 비활성화.")
            return
        if self._started:
            return
        try:
            from copilot import CopilotClient
            self._client = CopilotClient()
            await self._client.start()
            self._started = True
            print("[Copilot] ✅ CopilotClient 시작됨")
        except Exception as e:
            print(f"[Copilot] 시작 실패: {e}")
            self._client = None
            self._available = False

    async def stop(self):
        """CopilotClient 종료 (앱 종료 시)"""
        if self._client and self._started:
            try:
                await self._client.stop()
                print("[Copilot] CopilotClient 종료됨")
            except Exception as e:
                print(f"[Copilot] 종료 에러: {e}")
            finally:
                self._client = None
                self._started = False

    async def send(
        self,
        system_prompt: str,
        user_message: str,
        model: str = "gpt-4.1",
        timeout: float = 180.0,
    ) -> str | None:
        """프롬프트 전송 → 텍스트 응답 반환

        매 호출마다 세션을 생성하고 응답 후 세션은 GC됨.
        timeout: 응답 대기 시간 (기본 180초, 복잡한 프롬프트 대응)
        """
        if not self._client or not self._started:
            return None

        try:
            from copilot.session import PermissionHandler

            session = await self._client.create_session(
                model=model,
                on_permission_request=PermissionHandler.approve_all,
            )

            prompt = f"{system_prompt}\n\nUser request: {user_message}"
            response = await session.send_and_wait(prompt, timeout=timeout)

            if response and response.data:
                return response.data.content
            return None

        except TimeoutError:
            print(f"[Copilot 타임아웃] {model}: {timeout}초 초과")
            return None
        except Exception as e:
            print(f"[Copilot 에러] {model}: {str(e)[:120]}")
            return None

    def get_models(self) -> list[dict[str, str]]:
        """사용 가능한 모델 목록"""
        return COPILOT_MODELS

    def get_status(self) -> dict[str, Any]:
        """현재 상태"""
        from app.config import settings
        return {
            "available": self.is_available(),
            "started": self._started,
            "current_model": settings.copilot_model,
            "models": self.get_models() if self._started else [],
        }


# 모듈 레벨 싱글턴
copilot_manager = CopilotManager()
