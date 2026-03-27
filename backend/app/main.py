from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import chat, template


def create_app() -> FastAPI:
    app = FastAPI(
        title="NotionForge API",
        description="AI 기반 노션 템플릿 자동 생성 에이전트",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(chat.router)
    app.include_router(template.router)

    @app.get("/health")
    async def health_check():
        return {
            "status": "ok",
            "version": "0.1.0",
        }

    return app


app = create_app()
