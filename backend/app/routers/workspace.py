"""워크스페이스 관리 REST API 라우터"""

import re

from fastapi import APIRouter, HTTPException

from app.notion.client import NotionClient

router = APIRouter(prefix="/api/templates", tags=["workspace"])

_NOTION_ID = re.compile(r"^[a-f0-9]{32}$|^[a-f0-9-]{36}$")


def _validate_page_id(page_id: str) -> str:
    clean = page_id.replace("-", "")
    if not _NOTION_ID.match(page_id) and not re.match(r"^[a-f0-9]{32}$", clean):
        raise HTTPException(status_code=400, detail="잘못된 페이지 ID 형식입니다.")
    return page_id


@router.get("/search")
async def search_workspace(q: str = ""):
    """워크스페이스 검색"""
    from app.config import settings

    client = NotionClient(token=settings.notion_api_key, parent_page_id=settings.notion_parent_page_id)
    if client.mock_mode:
        return {"results": []}
    results = await client.search(query=q)
    return results


@router.post("/{page_id}/comment")
async def add_comment(page_id: str, text: str = ""):
    """페이지에 코멘트 추가"""
    from app.config import settings

    _validate_page_id(page_id)
    if not text or len(text) > 2000:
        raise HTTPException(status_code=400, detail="코멘트는 1~2000자여야 합니다.")
    client = NotionClient(token=settings.notion_api_key, parent_page_id=settings.notion_parent_page_id)
    result = await client.add_comment(page_id, text)
    return result


@router.post("/{page_id}/lock")
async def lock_page(page_id: str, locked: bool = True):
    """페이지 잠금/해제"""
    from app.config import settings

    _validate_page_id(page_id)
    client = NotionClient(token=settings.notion_api_key, parent_page_id=settings.notion_parent_page_id)
    result = await client.lock_page(page_id, locked)
    return result


@router.post("/{page_id}/archive")
async def archive_page(page_id: str):
    """페이지 아카이브"""
    from app.config import settings

    _validate_page_id(page_id)
    client = NotionClient(token=settings.notion_api_key, parent_page_id=settings.notion_parent_page_id)
    result = await client.archive_page(page_id)
    return result


@router.get("/history/recent")
async def get_generation_history(days: int = 7, limit: int = 50):
    """최근 생성 이력 조회"""
    from app.core.history import get_recent_history

    records = get_recent_history(days=days, limit=limit)
    return {"records": records, "count": len(records)}


@router.get("/memory/preferences")
async def get_preferences():
    """에이전트 메모리 — 유저 선호도 조회"""
    from app.agent.memory import memory
    return {"preferences": memory.get_all_preferences()}


@router.post("/memory/preferences")
async def set_preference(key: str = "", value: str = ""):
    """에이전트 메모리 — 유저 선호도 설정"""
    from app.agent.memory import memory
    if not key or len(key) > 50:
        raise HTTPException(status_code=400, detail="key는 1~50자여야 합니다.")
    memory.save_preference(key, value)
    return {"success": True}


@router.get("/memory/stats")
async def get_memory_stats():
    """에이전트 메모리 — 스킬 사용 통계"""
    from app.agent.memory import memory
    return {"stats": memory.get_skill_stats()}
