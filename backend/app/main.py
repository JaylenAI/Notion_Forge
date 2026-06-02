import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__
from app.config import settings
from app.core.logging_config import setup_logging
from app.core.middleware import RateLimitMiddleware, RequestIdMiddleware, SecurityHeadersMiddleware
from app.routers import ai, chat, oauth, recipes, skills, tasks, template, workspace

setup_logging(settings.log_level)

logger = logging.getLogger("notionforge")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 라이프사이클 관리 — 설정 검증 + Copilot + Graceful Shutdown"""
    # 시작 시 설정 검증
    if not settings.notion_api_key:
        logger.warning("NOTION_API_KEY 미설정 — Mock 모드로 동작합니다")
    if not settings.notion_parent_page_id:
        logger.warning("NOTION_PARENT_PAGE_ID 미설정 — 생성 기능 제한")

    logger.info(
        f"NotionForge 시작 — AI Provider: {settings.ai_provider}, Notion: {'ready' if settings.notion_ready else 'mock'}"
    )

    if settings.copilot_enabled:
        try:
            from app.core.copilot_client import copilot_manager

            await copilot_manager.start()
        except Exception as e:
            logger.warning(f"Copilot 시작 스킵: {e}")

    from app.core.history import cleanup_old_history

    cleanup_old_history(retention_days=30)

    yield

    # Graceful Shutdown
    logger.info("NotionForge 종료 중...")
    if settings.copilot_enabled:
        try:
            from app.core.copilot_client import copilot_manager

            await copilot_manager.stop()
        except Exception:
            pass
    logger.info("NotionForge 종료 완료")


def create_app() -> FastAPI:
    app = FastAPI(
        title="NotionForge API",
        description="AI 기반 노션 템플릿 자동 생성 에이전트",
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS — '*' + credentials 조합은 금지 (임의 오리진이 인증 컨텍스트로 요청 가능).
    # 운영자가 CORS_ORIGINS=["*"]로 설정하면 credentials를 자동 비활성화한다.
    cors_origins = settings.cors_origins
    allow_credentials = True
    if "*" in cors_origins:
        logger.warning("CORS_ORIGINS에 '*' 포함 — 보안상 allow_credentials를 비활성화합니다.")
        allow_credentials = False
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=allow_credentials,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Notion-Token", "X-Request-ID"],
    )

    app.add_middleware(RateLimitMiddleware, rpm=settings.rate_limit_rpm)
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)

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
            "version": __version__,
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
        durations: list[int] = []
        total_tokens = 0
        for r in records:
            m = r.get("metrics", {})
            skill = m.get("skill", "unknown")
            skills_used[skill] = skills_used.get(skill, 0) + 1
            d = m.get("total_duration_ms", 0)
            if d:
                durations.append(d)
            total_tokens += m.get("tokens_used", 0) or 0

        def _pct(data: list[int], q: float) -> int:
            if not data:
                return 0
            ordered = sorted(data)
            if len(ordered) == 1:
                return ordered[0]
            idx = min(len(ordered) - 1, int(round(q * (len(ordered) - 1))))
            return ordered[idx]

        return {
            "period": "7d",
            "total_generations": total,
            "success_count": success,
            "success_rate": round(success / total * 100, 1) if total > 0 else 0,
            "avg_duration_ms": round(sum(durations) / len(durations)) if durations else 0,
            "p50_duration_ms": _pct(durations, 0.5),
            "p95_duration_ms": _pct(durations, 0.95),
            "total_tokens_used": total_tokens,
            "top_skills": dict(sorted(skills_used.items(), key=lambda x: -x[1])[:10]),
        }

    @app.get("/metrics")
    async def prometheus_metrics():
        """Prometheus 텍스트 노출 포맷 (의존성 없이 직접 생성). 스크레이프용."""
        from fastapi.responses import PlainTextResponse

        from app.core.history import get_recent_history

        records = get_recent_history(days=7, limit=500)
        total = len(records)
        success = sum(1 for r in records if r.get("metrics", {}).get("success"))
        durations = [m for r in records if (m := r.get("metrics", {}).get("total_duration_ms", 0))]
        tokens = sum(r.get("metrics", {}).get("tokens_used", 0) or 0 for r in records)

        def _p95(data: list[int]) -> int:
            if not data:
                return 0
            ordered = sorted(data)
            return ordered[min(len(ordered) - 1, int(round(0.95 * (len(ordered) - 1))))]

        lines = [
            "# HELP notionforge_generations_total Total template generations (7d).",
            "# TYPE notionforge_generations_total counter",
            f"notionforge_generations_total {total}",
            "# HELP notionforge_generation_success_total Successful generations (7d).",
            "# TYPE notionforge_generation_success_total counter",
            f"notionforge_generation_success_total {success}",
            "# HELP notionforge_generation_duration_ms_p95 p95 generation latency (7d).",
            "# TYPE notionforge_generation_duration_ms_p95 gauge",
            f"notionforge_generation_duration_ms_p95 {_p95(durations)}",
            "# HELP notionforge_tokens_total Total LLM tokens used (7d).",
            "# TYPE notionforge_tokens_total counter",
            f"notionforge_tokens_total {tokens}",
        ]
        return PlainTextResponse("\n".join(lines) + "\n")

    return app


app = create_app()
