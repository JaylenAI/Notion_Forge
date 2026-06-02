from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Notion API
    notion_api_key: str = ""
    notion_parent_page_id: str = ""

    # Groq API (무료, gpt-oss-120b)
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-120b"

    # Gemini API (무료)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # Claude API (유료, 선택)
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-6"

    # Server
    backend_port: int = 9500
    frontend_port: int = 9501
    frontend_url: str = "http://localhost:9501"
    cors_origins: list[str] = ["http://localhost:9501", "http://localhost:3000"]
    rate_limit_rpm: int = 60  # HTTP IP 레이트리밋 (main.py가 Settings 우회하던 것 일원화)

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
    # 품질 게이트 (Phase A4) — 프리미엄 모드에서 유료급 미달 시 경고 고지. 기본 비활성(측정만).
    quality_gate_enabled: bool = False
    quality_gate_min_score: float = 60.0  # $20-49 진입 기준점
    # judge→repair (Phase 1) — LLM 심사 FAIL 시 약점 피드백으로 1회 재생성(evaluator-optimizer 완성)
    judge_repair_enabled: bool = True

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
