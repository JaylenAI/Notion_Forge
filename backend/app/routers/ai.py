"""AI 프로바이더 관련 REST API 라우터"""

from __future__ import annotations

from fastapi import APIRouter, Body

router = APIRouter(prefix="/api/templates", tags=["ai"])

_session_model: str | None = None


@router.post("/ai/detect-provider")
async def detect_provider(api_key: str = Body("", embed=True, max_length=500)):
    """API 키로 프로바이더 감지 + 모델 목록 조회"""
    from app.agent.providers.router import detect_provider_from_key

    if not api_key:
        return {"provider": "unknown", "models": [], "error": "API 키가 필요합니다."}

    raw = detect_provider_from_key(api_key)
    provider_aliases = {"claude": "anthropic", "gemini": "google"}
    provider = provider_aliases.get(raw, raw) if raw else "unknown"

    if provider == "unknown":
        return {"provider": "unknown", "models": [], "error": "알 수 없는 API 키 형식입니다."}

    models: list[dict] = []
    try:
        if provider == "openai":
            import httpx

            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0,
                )
                data = resp.json()
                models = [{"id": m["id"], "name": m["id"]} for m in data.get("data", []) if "gpt" in m["id"]]

        elif provider == "groq":
            import httpx

            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.groq.com/openai/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0,
                )
                data = resp.json()
                models = [{"id": m["id"], "name": m["id"]} for m in data.get("data", [])]

        elif provider == "anthropic":
            import httpx

            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.anthropic.com/v1/models",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                    },
                    timeout=10.0,
                )
                data = resp.json()
                models = [{"id": m["id"], "name": m["id"]} for m in data.get("data", [])]

        elif provider == "google":
            from google import genai

            client = genai.Client(api_key=api_key)
            model_list = []
            for model in client.models.list():
                if "gemini" in model.name.lower():
                    model_list.append(
                        {
                            "id": model.name,
                            "name": model.display_name or model.name,
                        }
                    )
            models = model_list

    except Exception as e:
        return {"provider": provider, "models": [], "error": f"모델 목록 조회 실패: {str(e)[:200]}"}

    return {"provider": provider, "models": models}


@router.get("/ai/copilot-status")
async def copilot_status():
    """Copilot SDK 상태 및 사용 가능 모델 조회"""
    try:
        from app.core.copilot_client import copilot_manager

        return copilot_manager.get_status()
    except ImportError:
        return {"available": False, "started": False, "models": []}


@router.post("/ai/copilot-model")
async def set_copilot_model(model: str = Body("gpt-4.1", embed=True)):
    """Copilot 모델 변경 (세션 단위 — 글로벌 설정 변경 없음)"""
    global _session_model
    allowed_models = ["gpt-4.1", "gpt-4.1-mini", "gpt-5-mini", "gpt-5.2", "claude-sonnet-4-5", "o3-mini", "o4-mini"]
    if model not in allowed_models:
        return {"error": f"허용되지 않는 모델입니다. 사용 가능: {', '.join(allowed_models)}"}
    _session_model = model
    return {"model": model, "status": "updated", "scope": "session"}


@router.get("/ai/current-model")
async def get_current_model():
    """현재 활성 모델 조회"""
    from app.config import settings

    return {
        "default_model": settings.copilot_model,
        "session_model": _session_model,
        "active": _session_model or settings.copilot_model,
    }
