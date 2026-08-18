# NotionForge — AI Notion Template Agent

> 🔴 **전역 프롬프트(`~/.claude/CLAUDE.md`)와 같은 말은 여기 적지 않는다.**
> 브랜치 흐름 · 커밋 형식 · 한글 커밋 · Co-Authored-By 금지 · PR · 릴리스 ·
> 머지 전 게이트 · 보고 규칙 · 에이전트 작업 규칙은 **거기가 정본**이다.
> 여기는 **이 레포에만 해당하는 것**과 **표준과 다르게 정한 것**만 적는다.
> 충돌하면 이 파일이 이긴다(전역 우선순위 ②).

---

## 0. 지금 무엇을 하는가

AI 기반 Notion 템플릿 자동 생성 에이전트. 자연어 입력 → 전문가급 Notion 워크스페이스 생성.

| 항목 | 값 |
|---|---|
| 목적 | **GitHub 오픈소스 배포** (SaaS 아님) |
| 라이선스 | MIT (공개) |
| 현재 아키텍처 | v0.1.6 (§3) |

---

## 1. 🔴 이 레포에서 절대 하지 말 것

- 🔴 **`push` 는 반드시 사용자 허락 후.** 커밋까지만 하고 확인 질문한다 —
  전역 §2 의 일괄 승인으로도 이 레포의 push 는 덮이지 않는다. **공개 레포이기 때문**이다.
- 🔴 **Notion API 버전을 한 벌로 합치지 말 것.** 쓰기는 `2022-06-28`, 읽기·뷰는 `2026-03-11`
  **듀얼 API** 다. 한쪽으로 통일하면 5-Pass 생성의 뷰 단계가 조용히 깨진다.
- 🔴 **사용자 입력을 InputGuardrail 없이 프롬프트에 넣지 말 것** (프롬프트 인젝션 방어선이다).

---

## 2. 명령

```bash
# Backend
cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 9500 --reload
# Frontend
cd frontend && npm run dev

# 머지 전 게이트 (전역 §3) — 이 레포에서는 이 넷이다
cd backend  && uv run pytest tests/ -v
cd backend  && uv run pytest tests/ --cov=app --cov-report=html
cd backend  && uv run ruff check . && uv run ruff format .
cd frontend && npm run lint

docker compose up --build
```

---

## 3. 구조

### 아키텍처 (v0.1.6)

```
User Input
  → InputGuardrail (프롬프트 인젝션 방어)
  → IntentAnalyzer (의도 분석)
  → SkillRouter (키워드 빠른경로 + LLM 정밀 분류)
  → Agent Loop (Plan-Execute-Reflect)
      → Tool Registry 11개 도구
          ├─ create_page / create_database / add_blocks
          ├─ create_columns / add_database_items / link_databases
          ├─ create_view / apply_color_theme / generate_cover
          ├─ create_worker / register_external_agent
      → Reflect (결과 자가 평가, 최대 3회 Re-plan)
  → PostProcessor (13종 자동 보정 + 구조 검증)
  → 5-Pass Creation (페이지→서브페이지→DB(레거시)→뷰(최신)→샘플 데이터 + 롤백)
```

### 디렉터리

```
backend/
  app/
    agent/            # AI Agent 핵심 (orchestrator, agent_loop, creation_executor)
    agent/providers/  # LLM Provider Strategy Pattern (5종)
    agent/tools/      # Tool Registry 11개 도구 (BaseTool 인터페이스)
    agent/prompts/    # 모듈화된 프롬프트 (.md)
    skills/           # 48개 도메인 스킬 (SKILL.md)
    notion/           # Notion API 클라이언트 (Mixin 패턴)
    routers/          # FastAPI 라우터
    core/             # 유틸리티 (logging, metrics, history)
    schemas/          # Pydantic 모델
  tests/
frontend/
  src/{components,stores,hooks,lib,types}/
```

---

## 4. 이 레포만의 사실

| 항목 | 값 |
|---|---|
| Backend | Python 3.11+ / FastAPI / uv |
| Frontend | React 19 / TypeScript 5.7 / Vite 7 / Zustand 5 / TailwindCSS 4 |
| AI Providers | Copilot SDK · Claude · Gemini · Groq · OpenAI (Strategy Pattern) |
| Notion | `notion-client` 2.x + httpx — **듀얼 API**: 쓰기 `2022-06-28` / 읽기·뷰 `2026-03-11` |
| 백엔드 포트 | 9500 |

---

## 5. 표준과 다른 것

- 🔴 **`push` 승인은 일괄 승인으로 덮이지 않는다** (§1). 공개 레포라 되돌릴 수 없다.
- **`main` 은 안정 버전만.** `dev` 에서 충분히 검증한 뒤 **버전 릴리스 시에만** 머지하고
  태그를 만든다 — 전역 §2-1 릴리스 순서를 그대로 쓰되, 이 레포는 릴리스가 아니면 머지하지 않는다.
- 브랜치 네이밍은 전역 §2 와 같다 (`feature/` · `fix/` · `refactor/` · `docs/`).
