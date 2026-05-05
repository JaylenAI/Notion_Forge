import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.logging_config import setup_logging
from app.routers import ai, chat, oauth, recipes, skills, tasks, template, workspace

setup_logging(settings.log_level)

logger = logging.getLogger("notionforge")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 Copilot SDK 라이프사이클 관리"""
    if settings.copilot_enabled:
        try:
            from app.core.copilot_client import copilot_manager

            await copilot_manager.start()
        except Exception as e:
            logger.warning(f"Copilot 시작 스킵: {e}")

    # 이력 보존 정책 — 30일 이상 된 파일 자동 정리
    from app.core.history import cleanup_old_history

    cleanup_old_history(retention_days=30)

    yield
    if settings.copilot_enabled:
        try:
            from app.core.copilot_client import copilot_manager

            await copilot_manager.stop()
        except Exception:
            pass


def create_app() -> FastAPI:
    app = FastAPI(
        title="NotionForge API",
        description="AI 기반 노션 템플릿 자동 생성 에이전트",
        version="8.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Notion-Token"],
    )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"},
        )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration:.2f}s)")
        return response

    app.include_router(chat.router)
    app.include_router(template.router)
    app.include_router(tasks.router)
    app.include_router(ai.router)
    app.include_router(workspace.router)
    app.include_router(recipes.router)
    app.include_router(oauth.router)
    app.include_router(skills.router)

    @app.get("/health")
    async def health_check():
        copilot_status = {}
        try:
            from app.core.copilot_client import copilot_manager

            copilot_status = copilot_manager.get_status()
        except ImportError:
            copilot_status = {"available": False}

        from app.core.history import get_recent_history

        recent = get_recent_history(days=1, limit=100)
        total = len(recent)
        success_count = sum(1 for r in recent if r.get("metrics", {}).get("success"))

        return {
            "status": "ok",
            "version": "8.0.0",
            "ai_provider": settings.ai_provider,
            "notion_ready": settings.notion_ready,
            "copilot": copilot_status,
            "features": 78,
            "skills": 48,
            "today_stats": {
                "total": total,
                "success": success_count,
                "success_rate": round(success_count / total * 100, 1) if total > 0 else 0,
            },
        }

    @app.get("/health/ready")
    async def readiness_check():
        """쿠버네티스/Docker 준비 상태 확인 — AI provider + Notion 연결 가능 여부"""
        checks = {
            "notion_configured": bool(settings.notion_api_key and settings.notion_parent_page_id),
            "ai_provider_configured": settings.ai_provider != "none",
        }
        all_ready = all(checks.values())
        return {"ready": all_ready, "checks": checks}

    @app.get("/health/live")
    async def liveness_check():
        """쿠버네티스 liveness — 서버 응답 가능 여부만"""
        return {"alive": True}

    @app.get("/api/metrics/summary")
    async def metrics_summary():
        """메트릭 요약 — 최근 7일 통계"""
        from app.core.history import get_recent_history

        records = get_recent_history(days=7, limit=500)
        total = len(records)
        success = sum(1 for r in records if r.get("metrics", {}).get("success"))

        skills_used: dict[str, int] = {}
        total_duration = 0
        for r in records:
            m = r.get("metrics", {})
            skill = m.get("skill", "unknown")
            skills_used[skill] = skills_used.get(skill, 0) + 1
            total_duration += m.get("total_duration_ms", 0)

        return {
            "period": "7d",
            "total_generations": total,
            "success_count": success,
            "success_rate": round(success / total * 100, 1) if total > 0 else 0,
            "avg_duration_ms": round(total_duration / total) if total > 0 else 0,
            "top_skills": dict(sorted(skills_used.items(), key=lambda x: -x[1])[:10]),
        }

    return app


app = create_app()
