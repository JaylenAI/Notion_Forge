"""템플릿 생성 REST API 라우터"""

from fastapi import APIRouter

from app.agent.blueprint_generator import generate_blueprint
from app.agent.orchestrator import AgentOrchestrator
from app.notion.client import NotionClient
from app.schemas.template import (
    TemplateGenerateRequest,
    TemplateGenerateResponse,
    TemplatePreviewRequest,
    TemplatePreviewResponse,
)

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.post("/generate", response_model=TemplateGenerateResponse)
async def generate_template(req: TemplateGenerateRequest):
    """템플릿 생성 (동기)"""
    agent = AgentOrchestrator(
        notion_token=req.notion_token,
        parent_page_id=req.parent_page_id,
    )

    result = None
    async for event in agent.process(req.prompt):
        if event["type"] == "complete":
            result = event.get("result", {})
        elif event["type"] == "question":
            return TemplateGenerateResponse(
                success=False,
                summary={"question": event["content"]},
            )

    if result:
        return TemplateGenerateResponse(
            success=True,
            notion_url=result.get("main_url"),
            page_id=result["pages"][0]["id"] if result.get("pages") else None,
            summary={
                "pages": len(result.get("pages", [])),
                "databases": len(result.get("databases", [])),
                "blocks": result.get("blocks", 0),
            },
        )

    return TemplateGenerateResponse(success=False)


@router.post("/preview", response_model=TemplatePreviewResponse)
async def preview_template(req: TemplatePreviewRequest):
    """Blueprint 미리보기 (생성 없이 구조만 확인)"""
    blueprint = await generate_blueprint(req.prompt)
    return TemplatePreviewResponse(blueprint=blueprint)


@router.get("/patterns")
async def list_patterns():
    """사용 가능한 템플릿 패턴 목록"""
    return {
        "patterns": [
            {"id": "dashboard", "name": "대시보드", "icon": "🏢", "description": "갤러리 뷰 + 칼럼 + 네비게이션"},
            {"id": "tracker", "name": "트래커", "icon": "✅", "description": "습관/목표/학습 추적"},
            {"id": "bookmark", "name": "북마크 사이트", "icon": "🔖", "description": "카테고리별 링크 정리"},
            {"id": "project", "name": "프로젝트 보드", "icon": "📊", "description": "태스크 관리 + 칸반"},
            {"id": "note", "name": "노트/기록", "icon": "📝", "description": "기록 수집 (Tea Note 스타일)"},
            {"id": "onboarding", "name": "온보딩 가이드", "icon": "👋", "description": "신입사원 인수인계"},
            {"id": "crm", "name": "CRM", "icon": "🤝", "description": "고객/영업 관리"},
        ]
    }


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
