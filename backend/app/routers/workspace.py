"""워크스페이스 관리 REST API 라우터"""

from fastapi import APIRouter

from app.notion.client import NotionClient

router = APIRouter(prefix="/api/templates", tags=["workspace"])


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

    client = NotionClient(token=settings.notion_api_key, parent_page_id=settings.notion_parent_page_id)
    result = await client.add_comment(page_id, text)
    return result


@router.post("/{page_id}/lock")
async def lock_page(page_id: str, locked: bool = True):
    """페이지 잠금/해제"""
    from app.config import settings

    client = NotionClient(token=settings.notion_api_key, parent_page_id=settings.notion_parent_page_id)
    result = await client.lock_page(page_id, locked)
    return result


@router.post("/{page_id}/archive")
async def archive_page(page_id: str):
    """페이지 아카이브"""
    from app.config import settings

    client = NotionClient(token=settings.notion_api_key, parent_page_id=settings.notion_parent_page_id)
    result = await client.archive_page(page_id)
    return result


@router.get("/history/recent")
async def get_generation_history(days: int = 7, limit: int = 50):
    """최근 생성 이력 조회"""
    from app.core.history import get_recent_history

    records = get_recent_history(days=days, limit=limit)
    return {"records": records, "count": len(records)}
