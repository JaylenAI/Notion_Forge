"""템플릿 생성 REST API 라우터"""

from fastapi import APIRouter, Body, UploadFile, File

from app.agent.blueprint_generator import generate_blueprint
from app.agent.orchestrator import AgentOrchestrator
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
        if event["type"] == "approval_request":
            # REST API에서는 자동 승인 (WebSocket이 아니므로 유저 입력 불가)
            agent.approve_creation(approved=True)
        elif event["type"] == "complete":
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


@router.post("/document-to-notion")
async def document_to_notion(file: UploadFile = File(...)):
    """문서 업로드 → 구조 분석 → 블루프린트 프리뷰

    지원: .txt, .md, .csv, .pdf
    """
    from app.agent.document_parser import parse_document, parse_pdf_bytes

    content_bytes = await file.read()
    filename = file.filename or "document.txt"
    ext = filename.rsplit(".", 1)[-1].lower()

    if ext == "pdf":
        parsed = parse_pdf_bytes(content_bytes)
    else:
        content_str = content_bytes.decode("utf-8", errors="replace")
        parsed = parse_document(content_str, filename)

    # CSV인 경우 바로 블루프린트 생성
    if parsed.get("properties"):
        db_title = parsed.get("db_title", "Imported Data")
        blueprint = {
            "version": "3.0",
            "metadata": {"title": db_title, "template_type": "custom", "color_theme": "blue"},
            "main_page": {"title": db_title, "icon": "📄"},
            "blocks": [
                {"type": "callout", "text": f"{parsed['hint']}", "icon": "📄", "color": "blue_background"},
                {"type": "heading_1", "text": f"📊 {db_title}"},
                {"type": "database_ref", "db_index": 0},
            ],
            "databases": [{
                "title": db_title, "is_inline": True,
                "properties": parsed["properties"],
                "views": ["table"],
                "sample_items": parsed.get("sample_items", []),
            }],
            "sub_pages": [],
        }
        return {"success": True, "blueprint": blueprint, "hint": parsed["hint"]}

    # MD/텍스트: AI에게 전달할 컨텍스트 생성
    hint = parsed.get("hint", "")
    text_content = parsed.get("text_content", "")
    blocks = parsed.get("blocks", [])

    # AI에게 문서 기반 템플릿 설계 요청
    ai_prompt = f"이 문서를 기반으로 노션 템플릿을 만들어줘:\n\n{text_content[:2000]}"
    bp = await generate_blueprint(ai_prompt)

    # MD 블록이 있으면 블루프린트에 추가
    if blocks:
        bp["blocks"] = blocks + bp.get("blocks", [])

    return {"success": True, "blueprint": bp, "hint": hint}


@router.post("/blueprint/import")
async def import_blueprint(blueprint: dict = Body(...)):
    """Blueprint JSON 가져오기 → 실제 Notion 생성"""
    from app.config import settings as cfg

    agent = AgentOrchestrator(
        notion_token=cfg.notion_api_key,
        parent_page_id=cfg.notion_parent_page_id,
    )

    # blueprint를 직접 실행
    result = await agent._execute_blueprint(blueprint)
    return {
        "success": True,
        "notion_url": result.get("main_url"),
        "summary": {
            "pages": len(result.get("pages", [])),
            "databases": len(result.get("databases", [])),
            "blocks": result.get("blocks", 0),
        },
    }


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
