# NotionForge

> AI 채팅으로 노션 템플릿을 자동 생성하는 오픈소스 에이전트

## 프로젝트 개요

**NotionForge**는 사용자가 자연어로 원하는 노션 템플릿을 설명하면, AI Agent가 Notion API를 통해 완성된 템플릿을 자동으로 생성해주는 서비스입니다.

> **소속**: 가짜연구소 - "나만의 자동화 AI Agent 만들기" 프로젝트
> **브랜치**: `dev` (개발 브랜치)

---

## 빠른 시작

### 사전 요구사항

| 도구 | 최소 버전 | 확인 명령 |
|------|----------|----------|
| Docker | 24+ | `docker --version` |
| Docker Compose | v2+ | `docker compose version` |
| uv | 최신 | `uv --version` |
| Node.js | 18+ | `node --version` |

### 1단계: 클론 & 환경 설정

```bash
git clone https://github.com/JaylenAI/notion_ai_agent.git
cd notion_ai_agent
git checkout dev
cp .env.example .env
```

### 2단계: .env 설정

```env
# 필수
NOTION_API_KEY=ntn_xxxx          # https://notion.so/my-integrations
NOTION_PARENT_PAGE_ID=xxxxx      # 템플릿 생성할 부모 페이지 ID
GROQ_API_KEY=gsk_xxxx            # https://console.groq.com/keys (무료)

# 선택 (없으면 Mock 모드)
ANTHROPIC_API_KEY=               # Claude API (유료)
GEMINI_API_KEY=                  # Gemini API (무료)
```

### 3단계: 실행

**방법 1: Docker (권장)**
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

**방법 2: 로컬 (uv + npm)**
```bash
# Backend (터미널 1)
cd backend
uv sync
uv run uvicorn app.main:app --port 9500 --reload

# Frontend (터미널 2)
cd frontend
npm install
npm run dev
```

**방법 3: Makefile**
```bash
make install    # 의존성 설치
make dev        # Docker 개발 환경
make dev-backend  # 백엔드만
make dev-frontend # 프론트엔드만
make test       # 테스트 실행
```

### 4단계: 접속

| 서비스 | URL |
|--------|-----|
| 프론트엔드 (채팅 UI) | http://localhost:9501 |
| 백엔드 API | http://localhost:9500 |
| API 문서 (Swagger) | http://localhost:9500/docs |

---

## 주요 기능

- **채팅 기반 템플릿 생성**: 자연어로 설명 → AI가 분석 → Notion에 자동 생성
- **7가지 템플릿 패턴**: 대시보드, 트래커, 북마크, 프로젝트, 노트, 온보딩, CRM
- **AI 의도 분석**: Groq (무료) / Gemini / Claude 지원 + Mock 폴백
- **스킬 시스템**: `.md` 파일로 템플릿 패턴 정의 (확장 가능)
- **실시간 진행률**: WebSocket으로 생성 과정 실시간 표시
- **색상 테마**: 8가지 색상 (blue, orange, green, red, purple, pink, yellow, gray)

---

## 프로젝트 구조

```
NotionForge/
├── docker-compose.yml / docker-compose.dev.yml
├── Makefile
├── .env.example
├── docs/                          # 기획/기술 문서 (10개)
│
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml (uv)
│   ├── app/
│   │   ├── main.py                # FastAPI 진입점
│   │   ├── config.py              # 환경변수 (Groq/Gemini/Claude 자동 선택)
│   │   ├── core/                  # 예외, 의존성
│   │   ├── agent/                 # AI Agent 핵심
│   │   │   ├── orchestrator.py    # 메인 파이프라인
│   │   │   ├── intent_analyzer.py # 의도 분석 (Groq/Gemini/Claude/Mock)
│   │   │   ├── blueprint_generator.py  # 구조 설계
│   │   │   └── tools/             # 8개 Tool (create_page, create_database 등)
│   │   ├── notion/                # Notion API 클라이언트 + Rate Limiter
│   │   ├── skills/                # .md 스킬 파일 (8개)
│   │   ├── routers/               # API 라우터 (REST + WebSocket)
│   │   └── schemas/               # Pydantic 모델
│   └── tests/                     # 28개 테스트 (100% 통과)
│
└── frontend/
    ├── Dockerfile
    ├── src/
    │   ├── components/
    │   │   ├── chat/              # ChatWindow, MessageBubble, InputBar
    │   │   ├── layout/            # MainLayout (사이드바 + 채팅)
    │   │   ├── settings/          # SettingsPanel (API 키 입력)
    │   │   └── common/            # ProgressBar, ErrorBoundary
    │   ├── stores/chatStore.ts    # Zustand + WebSocket + localStorage
    │   └── types/index.ts
    └── ...
```

---

## 기술 스택

| 레이어 | 기술 |
|--------|------|
| **Backend** | FastAPI + Python 3.11 + uv |
| **AI** | Groq (gpt-oss-120b, 무료) / Gemini Flash / Claude Sonnet |
| **Notion** | Notion API (notion-client 3.x) |
| **Frontend** | React 19 + Vite 7 + TailwindCSS 4 + Zustand 5 |
| **컨테이너** | Docker + Docker Compose |
| **CI/CD** | GitHub Actions |

---

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/health` | 헬스체크 |
| GET | `/api/templates/patterns` | 사용 가능한 패턴 목록 (7개) |
| POST | `/api/templates/preview` | Blueprint 미리보기 |
| POST | `/api/templates/generate` | 템플릿 생성 |
| WS | `/ws/chat` | 실시간 채팅 |

---

## 스킬 시스템

`.md` 파일로 정의된 템플릿 패턴. 각 스킬은 트리거 조건, 페이지 구조, DB 스키마, 샘플 데이터를 포함.

```
backend/app/skills/
├── content-writing/        # 공통 콘텐츠 작성 가이드
├── template-dashboard/     # 대시보드 (To-Do List)
├── template-tracker/       # 습관 트래커
├── template-bookmark/      # 북마크 사이트
├── template-onboarding/    # 온보딩 가이드
├── template-note/          # 노트/기록 (Tea Note)
├── template-project/       # 프로젝트 보드
└── template-crm/           # CRM
```

---

## 비용

| 항목 | 비용 |
|------|------|
| Notion API | 무료 |
| Groq API (gpt-oss-120b) | 무료 |
| Docker / uv / Vite | 무료 |
| **합계** | **$0** |

---

## 문서

| 문서 | 설명 |
|------|------|
| [기획서 + 시장조사](docs/PLANNING.md) | 프로젝트 WHY |
| [유저 시나리오](docs/USER_SCENARIOS.md) | 사용자 여정 + 대화 예시 |
| [아키텍처](docs/ARCHITECTURE.md) | 시스템 설계 + Notion API 분석 |
| [Agent 설계](docs/AGENT_DESIGN.md) | AI Agent + Tools + 프롬프트 |
| [API 명세](docs/API.md) | REST/WebSocket 엔드포인트 |
| [세팅 + 배포](docs/SETUP.md) | 환경 세팅 + Docker + 배포 |
| [개발 계획](docs/DEVELOPMENT_PLAN.md) | 모듈별 기능 + 로드맵 |
| [테스트 + QA](docs/TEST_GUIDE.md) | 테스트 실행 + 품질 체크리스트 |
| [인수인계](docs/ONBOARDING.md) | 합류자 가이드 |
| [변경 이력](docs/CHANGELOG.md) | 변경사항 + 회고 |

---

## 라이선스

MIT License
