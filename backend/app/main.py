import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import chat, template, recipes, oauth, skills

from app.core.logging_config import setup_logging

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
        version="6.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}")
        return JSONResponse(
            status_code=500,
            content={"error": str(exc), "detail": "Internal server error"},
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
        return {
            "status": "ok",
            "version": "6.1.0",
            "ai_provider": settings.ai_provider,
            "notion_ready": settings.notion_ready,
            "copilot": copilot_status,
            "features": 74,
        }

    return app


app = create_app()
