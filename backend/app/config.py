from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Notion API
    notion_api_key: str = ""
    notion_parent_page_id: str = ""

    # Groq API (무료, gpt-oss-120b)
    groq_api_key: str = ""

    # Gemini API (무료)
    gemini_api_key: str = ""

    # Claude API (유료, 선택)
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-6"

    # Server
    backend_port: int = 9500
    frontend_port: int = 9501
    frontend_url: str = "http://localhost:9501"
    cors_origins: list[str] = ["http://localhost:9501", "http://localhost:3000"]

    # Optional
    unsplash_access_key: str = ""
    log_level: str = "INFO"

    # Notion OAuth (선택 — 토큰 복붙 대신 OAuth 연동)
    notion_oauth_client_id: str = ""
    notion_oauth_client_secret: str = ""
    notion_oauth_redirect_uri: str = "http://localhost:9500/api/oauth/callback"

    # Copilot SDK (API 키 불필요, GitHub Copilot 구독 인증)
    copilot_enabled: bool = True
    copilot_model: str = "gpt-4.1"

    # Guardrail 설정
    input_min_length: int = 2
    input_max_length: int = 2000
    approval_timeout_seconds: int = 60
    gen_eval_max_retries: int = 3
    # 세션당 LLM 호출 상한 (비용 폭주 방지). Gen-Eval·멀티에이전트·AgentLoop 누적 호출의 안전망.
    max_llm_calls_per_session: int = 40
    # 품질 LLM 심사 (Phase A1) — 생성 후 주관적 품질 PASS/FAIL 평가. 비용 1콜/생성, 비차단.
    enable_llm_judge: bool = True

    @property
    def ai_provider(self) -> str:
        """사용할 AI 프로바이더 결정 (우선순위: Copilot > Claude > Gemini > Groq > Mock)"""
        if self.copilot_enabled:
            try:
                from app.core.copilot_client import copilot_manager

                if copilot_manager.is_available():
                    return "copilot"
            except ImportError:
                pass
        if self.anthropic_api_key:
            return "claude"
        if self.gemini_api_key:
            return "gemini"
        if self.groq_api_key:
            return "groq"
        return "mock"

    @property
    def mock_mode(self) -> bool:
        return self.ai_provider == "mock"

    @property
    def notion_ready(self) -> bool:
        return bool(self.notion_api_key and self.notion_parent_page_id)

    model_config = {"env_file": ["../.env", ".env"], "env_file_encoding": "utf-8"}


settings = Settings()
