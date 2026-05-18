"""Notion OAuth 연동 라우터 — CSRF state 검증 포함

환경변수:
  NOTION_OAUTH_CLIENT_ID
  NOTION_OAUTH_CLIENT_SECRET
  NOTION_OAUTH_REDIRECT_URI (기본: http://localhost:9500/api/oauth/callback)
  FRONTEND_URL (기본: http://localhost:9501)
"""

import logging
import secrets
import time
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from app.config import settings

logger = logging.getLogger("notionforge.oauth")

router = APIRouter(prefix="/api/oauth", tags=["oauth"])

NOTION_AUTH_URL = "https://api.notion.com/v1/oauth/authorize"
NOTION_TOKEN_URL = "https://api.notion.com/v1/oauth/token"

STATE_TTL = 300
MAX_PENDING_STATES = 1000
_pending_states: dict[str, float] = {}

EXCHANGE_CODE_TTL = 60
_exchange_codes: dict[str, dict] = {}


def _cleanup_expired_states() -> None:
    now = time.time()
    expired = [s for s, ts in _pending_states.items() if now - ts > STATE_TTL]
    for s in expired:
        del _pending_states[s]
    expired_codes = [c for c, d in _exchange_codes.items() if now - d["created"] > EXCHANGE_CODE_TTL]
    for c in expired_codes:
        del _exchange_codes[c]


@router.get("/authorize")
async def authorize():
    """Notion OAuth 인증 시작 — CSRF state 포함 리디렉트"""
    client_id = settings.notion_oauth_client_id
    redirect_uri = settings.notion_oauth_redirect_uri

    if not client_id:
        return {"error": "NOTION_OAUTH_CLIENT_ID가 설정되지 않았습니다. .env 파일을 확인하세요."}

    _cleanup_expired_states()

    if len(_pending_states) >= MAX_PENDING_STATES:
        return {"error": "인증 요청이 너무 많습니다. 잠시 후 다시 시도해주세요."}

    state = secrets.token_urlsafe(32)
    _pending_states[state] = time.time()

    params = urlencode(
        {
            "client_id": client_id,
            "response_type": "code",
            "owner": "user",
            "redirect_uri": redirect_uri,
            "state": state,
        }
    )
    return RedirectResponse(url=f"{NOTION_AUTH_URL}?{params}")


@router.get("/callback")
async def callback(code: str = "", error: str = "", state: str = ""):
    """Notion OAuth 콜백 — state 검증 + 토큰 교환"""
    frontend_url = settings.frontend_url

    if error:
        return RedirectResponse(url=f"{frontend_url}?oauth_error={error}")

    if not code:
        raise HTTPException(status_code=400, detail="인증 코���가 없습니다.")

    _cleanup_expired_states()

    if not state or state not in _pending_states:
        raise HTTPException(status_code=403, detail="CSRF 검증 실패. 인증을 다시 시도해주세요.")

    state_created = _pending_states.pop(state)
    if time.time() - state_created > STATE_TTL:
        raise HTTPException(status_code=403, detail="인증 세션이 만료되었습니다. 다시 시도해주세요.")

    client_id = settings.notion_oauth_client_id
    client_secret = settings.notion_oauth_client_secret
    redirect_uri = settings.notion_oauth_redirect_uri

    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="OAuth 클라이언트 설정이 없습니다.")

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            NOTION_TOKEN_URL,
            json={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
            },
            auth=(client_id, client_secret),
            headers={"Content-Type": "application/json"},
            timeout=10.0,
        )

        if resp.status_code != 200:
            logger.warning(f"OAuth 토큰 교환 실패: {resp.status_code}")
            raise HTTPException(status_code=502, detail="토큰 교환에 실패했습니다. 다시 시도해주세요.")

        token_data = resp.json()

    access_token = token_data.get("access_token", "")
    workspace_name = token_data.get("workspace_name", "")
    workspace_id = token_data.get("workspace_id", "")

    exchange_code = secrets.token_urlsafe(48)
    _exchange_codes[exchange_code] = {
        "access_token": access_token,
        "workspace_name": workspace_name,
        "workspace_id": workspace_id,
        "created": time.time(),
    }

    params = urlencode({"code": exchange_code})
    return RedirectResponse(url=f"{frontend_url}?oauth_callback=true&{params}")


@router.post("/exchange")
async def exchange_code(code: str = ""):
    """일회용 코드 → OAuth 토큰 교환 (토큰이 URL에 노출되지 않도록 보호)"""
    if not code or code not in _exchange_codes:
        _cleanup_expired_states()
        raise HTTPException(status_code=400, detail="유효하지 않거나 만료된 인증 코드입니다.")

    data = _exchange_codes.pop(code)
    _cleanup_expired_states()

    if time.time() - data["created"] > EXCHANGE_CODE_TTL:
        raise HTTPException(status_code=410, detail="인증 코드가 만료되었습니다. 다시 시도해주세요.")

    return {
        "oauth_token": data["access_token"],
        "workspace_name": data["workspace_name"],
        "workspace_id": data["workspace_id"],
    }


@router.get("/status")
async def oauth_status():
    """OAuth 설정 상태 확인"""
    return {
        "oauth_configured": bool(settings.notion_oauth_client_id),
        "redirect_uri": settings.notion_oauth_redirect_uri,
        "frontend_url": settings.frontend_url,
    }
