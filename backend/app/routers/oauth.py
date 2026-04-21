"""Notion OAuth 연동 라우터

환경변수:
  NOTION_OAUTH_CLIENT_ID
  NOTION_OAUTH_CLIENT_SECRET
  NOTION_OAUTH_REDIRECT_URI (기본: http://localhost:9500/api/oauth/callback)
  FRONTEND_URL (기본: http://localhost:9501)
"""

import logging

import httpx
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.config import settings

logger = logging.getLogger("notionforge.oauth")

router = APIRouter(prefix="/api/oauth", tags=["oauth"])

NOTION_AUTH_URL = "https://api.notion.com/v1/oauth/authorize"
NOTION_TOKEN_URL = "https://api.notion.com/v1/oauth/token"


@router.get("/authorize")
async def authorize():
    """Notion OAuth 인증 시작 — 브라우저 리디렉트"""
    client_id = settings.notion_oauth_client_id
    redirect_uri = settings.notion_oauth_redirect_uri

    if not client_id:
        return {"error": "NOTION_OAUTH_CLIENT_ID가 설정되지 않았습니다. .env 파일을 확인하세요."}

    auth_url = (
        f"{NOTION_AUTH_URL}"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&owner=user"
        f"&redirect_uri={redirect_uri}"
    )
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def callback(code: str = "", error: str = ""):
    """Notion OAuth 콜백 — 토큰 교환"""
    frontend_url = settings.frontend_url

    if error:
        return RedirectResponse(url=f"{frontend_url}?oauth_error={error}")

    if not code:
        return {"error": "인증 코드가 없습니다."}

    client_id = settings.notion_oauth_client_id
    client_secret = settings.notion_oauth_client_secret
    redirect_uri = settings.notion_oauth_redirect_uri

    if not client_id or not client_secret:
        return {"error": "OAuth 클라이언트 설정이 없습니다."}

    # 토큰 교환
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
            return {"error": f"토큰 교환 실패: {resp.text[:200]}"}

        token_data = resp.json()

    # 프론트엔드로 리디렉트 (토큰 전달)
    access_token = token_data.get("access_token", "")
    workspace_name = token_data.get("workspace_name", "")
    workspace_id = token_data.get("workspace_id", "")

    return RedirectResponse(
        url=(
            f"{frontend_url}"
            f"?oauth_token={access_token}"
            f"&workspace_name={workspace_name}"
            f"&workspace_id={workspace_id}"
        )
    )


@router.get("/status")
async def oauth_status():
    """OAuth 설정 상태 확인"""
    return {
        "oauth_configured": bool(settings.notion_oauth_client_id),
        "redirect_uri": settings.notion_oauth_redirect_uri,
        "frontend_url": settings.frontend_url,
    }
