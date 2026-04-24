# NotionForge - AI Notion Template Agent

## Project Overview
AI 기반 Notion 템플릿 자동 생성 에이전트. 자연어 입력 → 전문가급 Notion 워크스페이스 생성.
**목적**: GitHub 오픈소스 배포 (SaaS 아님)

## Tech Stack
- **Backend**: Python 3.11+ / FastAPI / uv
- **Frontend**: React 19 / TypeScript 5.7 / Vite 7 / Zustand 5 / TailwindCSS 4
- **AI Providers**: Copilot SDK, Claude, Gemini, Groq, OpenAI (Strategy Pattern)
- **Notion**: notion-client 2.x + httpx (Views API 2025-09-03)

## Git Branch Strategy (Git Flow 변형)

### 브랜치 구조
```
main          ← 안정 버전만. 태그로 버전 관리 (v8.0.0, v8.1.0...)
  └── dev     ← 통합 브랜치. feature들이 여기로 머지됨
       ├── feature/agent-loop      ← 기능 브랜치
       ├── feature/skill-upgrade   ← 기능 브랜치
       ├── fix/websocket-bug       ← 버그 수정
       └── refactor/provider-wire  ← 리팩토링
```

### 규칙 (절대 위반 금지)
1. **main에 직접 커밋 금지** — dev에서 충분히 검증 후 머지만 허용
2. **feature 브랜치는 dev에서 생성** — `git checkout -b feature/xxx dev`
3. **feature 완료 → dev로 PR/머지** — 기능 검증 후 dev에 취합
4. **버전 릴리스 시에만 dev → main 머지** — 태그 생성 필수
5. **커밋 메시지 한글** — `feat: 기능설명` / `fix: 버그설명` 등
6. **AI 참여 흔적 금지** — Co-Authored-By, AI 관련 문구 절대 포함 X
7. **push는 반드시 사용자 허락 후** — 커밋까지만 하고 확인 질문

### 브랜치 네이밍
- `feature/기능명` — 새 기능 개발
- `fix/버그명` — 버그 수정
- `refactor/대상` — 리팩토링
- `docs/문서명` — 문서 작업

### 머지 전 체크리스트
- [ ] 테스트 통과 (pytest)
- [ ] 린트 통과 (ruff / eslint)
- [ ] 타입 체크 통과
- [ ] 관련 문서 업데이트

## Development Commands
```bash
# Backend
cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 9500 --reload

# Frontend
cd frontend && npm run dev

# Test
cd backend && uv run pytest tests/ -v
cd backend && uv run pytest tests/ --cov=app --cov-report=html

# Lint
cd backend && uv run ruff check . && uv run ruff format .
cd frontend && npm run lint

# Docker
docker compose up --build
```

## Architecture (v8.0 목표)
```
User Input
  → InputGuardrail (프롬프트 인젝션 방어)
  → IntentAnalyzer (의도 분석)
  → SkillRouter (LLM function calling 기반 스킬 선택)
  → PlannerAgent (Plan-Execute 패턴)
      → Tool Registry (LLM이 도구 선택)
          ├─ create_database
          ├─ add_blocks
          ├─ create_view
          ├─ add_sample_data
          ├─ create_sub_page
          └─ modify_template
      → ReflectorAgent (결과 자가 평가)
      → 만족? → Done / 불만족? → Re-plan (최대 3회)
  → QualityValidator (3계층 검증)
  → NotionExecutor (5-Pass 생성 + 롤백)
```

## Key Directories
```
backend/
  app/
    agent/           # AI Agent 핵심 (orchestrator, planner, reflector)
    agent/providers/  # LLM Provider Strategy Pattern
    agent/tools/      # Tool Registry (BaseTool 인터페이스)
    agent/prompts/    # 모듈화된 프롬프트 (.md)
    skills/           # 48+ 도메인 스킬 (SKILL.md)
    notion/           # Notion API 클라이언트
    routers/          # FastAPI 라우터
    core/             # 유틸리티 (logging, metrics, history)
    schemas/          # Pydantic 모델
  tests/              # pytest 테스트
frontend/
  src/
    components/       # React 컴포넌트
    stores/           # Zustand 상태관리
    hooks/            # 커스텀 훅
    lib/              # 유틸리티
    types/            # TypeScript 타입
```
