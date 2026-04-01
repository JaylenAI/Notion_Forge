"""템플릿 생성 REST API 라우터"""

from fastapi import APIRouter, Body

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


@router.post("/ai/detect-provider")
async def detect_provider(api_key: str = Body("", embed=True)):
    """API 키로 프로바이더 감지 + 모델 목록 조회"""
    if not api_key:
        return {"provider": "unknown", "models": [], "error": "API 키가 필요합니다."}

    # 키 접두사로 프로바이더 감지
    provider = "unknown"
    if api_key.startswith("sk-ant-"):
        provider = "anthropic"
    elif api_key.startswith("sk-proj-") or api_key.startswith("sk-"):
        provider = "openai"
    elif api_key.startswith("gsk_"):
        provider = "groq"
    elif api_key.startswith("AIza"):
        provider = "google"

    if provider == "unknown":
        return {"provider": "unknown", "models": [], "error": "알 수 없는 API 키 형식입니다."}

    # 프로바이더별 모델 목록 조회
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
                models = [
                    {"id": m["id"], "name": m["id"]}
                    for m in data.get("data", [])
                    if "gpt" in m["id"]
                ]

        elif provider == "groq":
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.groq.com/openai/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0,
                )
                data = resp.json()
                models = [
                    {"id": m["id"], "name": m["id"]}
                    for m in data.get("data", [])
                ]

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
                models = [
                    {"id": m["id"], "name": m["id"]}
                    for m in data.get("data", [])
                ]

        elif provider == "google":
            from google import genai
            client = genai.Client(api_key=api_key)
            model_list = []
            for model in client.models.list():
                if "gemini" in model.name.lower():
                    model_list.append({
                        "id": model.name,
                        "name": model.display_name or model.name,
                    })
            models = model_list

    except Exception as e:
        return {"provider": provider, "models": [], "error": f"모델 목록 조회 실패: {str(e)[:200]}"}

    return {"provider": provider, "models": models}


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
