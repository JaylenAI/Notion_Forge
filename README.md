# NotionForge

> AI 채팅으로 노션 템플릿을 자동 생성하는 오픈소스 에이전트

## 프로젝트 개요

**NotionForge**는 사용자가 자연어로 원하는 노션 템플릿을 설명하면, AI Agent가 Notion API를 통해 완성된 템플릿을 자동으로 생성해주는 서비스입니다.

> **소속**: 가짜연구소 - "나만의 자동화 AI Agent 만들기" 프로젝트
> **브랜치**: `dev-2` (AI 자유 설계 + 12개 스킬, 최신) | `dev` (하드코딩 방식)

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
git checkout dev-2    # AI 자유 설계 (최신) | dev: 하드코딩 방식
cp .env.example .env
```

### 2단계: .env 설정

```env
# 필수
NOTION_API_KEY=ntn_xxxx          # https://notion.so/my-integrations
NOTION_PARENT_PAGE_ID=xxxxx      # 템플릿 생성할 부모 페이지 ID

# AI 프로바이더 (하나 이상 필수, 없으면 Mock 모드)
GEMINI_API_KEY=                  # Gemini API (무료, 기본)
GROQ_API_KEY=gsk_xxxx            # https://console.groq.com/keys (무료)
ANTHROPIC_API_KEY=               # Claude API (유료, 최고 품질)
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

### AI 자유 설계 시스템
- **채팅 기반 생성**: 자연어 → AI가 blocks[] + databases[] 직접 설계 → Notion에 자동 생성
- **12개 스킬**: track, collect, manage, plan, organize, guide, hub, finance, journal, content, learn, crm
- **4개 AI 프로바이더**: Gemini (기본) / Groq / Claude / OpenAI — 동적 모델 선택
- **실시간 스트리밍**: 생성 과정을 단계별로 표시 (의도 분석 → 설계 → 페이지 → DB → 뷰 → 완료)
- **스마트 폴백**: AI 실패 시 키워드 기반 6개 템플릿 자동 선택

### Notion API 전체 지원 (74개 기능)
- **블록 30+종**: heading, callout, toggle, quote, code, table, equation, tab, synced_block 등
- **인라인 서식**: bold, italic, underline, strikethrough, code, link, 색상, 멘션
- **미디어**: image, video, audio, file, pdf, bookmark, embed (Figma, GitHub, Loom 등 12개)
- **DB 뷰 10개**: table, gallery, calendar, board, timeline, list, chart, form, map, dashboard
- **DB 속성 전체**: select, multi_select, status, relation, rollup, formula, unique_id, people 등

### 프론트엔드
- **다크/라이트 테마**: CSS 변수 기반 전체 테마 시스템 + 토글
- **5개 페이지**: Dashboard, Library, Integrations, Profile, Support
- **프롬프트 스타터**: 6개 추천 템플릿 원클릭 생성
- **프롬프트 라이브러리**: 4개 카테고리 × 18개 프롬프트 템플릿 (Business/Personal/Content/Learning)
- **노션 스타일 렌더러**: 14개 블록 + 4개 DB 뷰 (Table/Board/Calendar/Gallery) 미리보기
- **Library 자동 저장**: 생성된 템플릿 자동 보관 + 검색/필터/정렬
- **AI 모델 선택**: 프로바이더 자동 감지 + 모델 목록 API
- **채팅 마크다운 렌더링**: AI 응답에 bold, 리스트, 코드블록, 테이블 등 렌더링
- **채팅 세션 관리**: 세션 자동저장/복원/삭제, 최대 50개 히스토리
- **키보드 단축키**: ⌘N 새 템플릿, ⌘K 커맨드 팔레트
- **미리보기 줌**: 50%~150% 줌 인/아웃
- **모바일 반응형**: 768px 이하 탭 전환 UI, 오버레이 사이드바
- **토스트 알림**: 저장/연결/에러 시 피드백
- **생성 취소**: 진행 중인 템플릿 생성 취소 가능

---

## 프로젝트 구조

```
NotionForge/
├── docker-compose.yml / docker-compose.dev.yml
├── Makefile
├── .env.example
├── docs/                          # 기획/기술 문서
│
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI 진입점
│   │   ├── config.py              # AI 프로바이더 자동 선택
│   │   ├── agent/
│   │   │   ├── orchestrator.py    # 실시간 스트리밍 파이프라인
│   │   │   ├── intent_analyzer.py # 의도 분석 (4개 프로바이더)
│   │   │   ├── blueprint_generator.py  # AI 자유 설계 + 스마트 폴백
│   │   │   └── tools/             # 8개 Tool
│   │   ├── notion/                # Notion API 클라이언트 (74개 기능)
│   │   ├── skills/                # 12개 스킬 (.md)
│   │   │   ├── track/   collect/   manage/   plan/
│   │   │   ├── organize/ guide/    hub/
│   │   │   ├── finance/  journal/  content/
│   │   │   └── learn/    crm/
│   │   ├── routers/               # REST + WebSocket
│   │   └── schemas/
│   └── tests/                     # 39개 테스트 (100% 통과)
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── dashboard/         # ChatPanel, LivePreview, NotionRenderer
    │   │   ├── library/           # 템플릿 자동 저장 + 검색/필터
    │   │   ├── integrations/      # Notion + AI 모델 설정
    │   │   ├── profile/           # 연결 상태 + 통계
    │   │   ├── support/           # FAQ + 문서
    │   │   └── layout/            # AppLayout (사이드바 + 상단 네비)
    │   ├── stores/
    │   │   ├── chatStore.ts       # Zustand + WebSocket + 세션 관리
    │   │   └── themeStore.ts      # 다크/라이트 테마 상태
    │   ├── lib/
    │   │   ├── api.ts             # API 유틸
    │   │   ├── utils.ts           # 공통 유틸
    │   │   └── timeago.ts         # 상대시간 ("3분 전")
    │   └── types/index.ts
    └── ...
```

---

## 기술 스택

| 레이어 | 기술 |
|--------|------|
| **Backend** | FastAPI + Python 3.11 + uv |
| **AI** | Gemini 2.5 Flash (기본) / Groq / Claude / OpenAI |
| **Notion** | notion-client 3.x + httpx (Legacy 2022-06-28 + Views 2025-09-03) |
| **Frontend** | React 19 + Vite 7 + TailwindCSS 4 + Zustand 5 + react-markdown |
| **컨테이너** | Docker + Docker Compose |
| **CI/CD** | GitHub Actions |

---

## 스킬 시스템 (12개)

| 스킬 | 용도 | 뷰 |
|------|------|-----|
| track | 습관/운동/공부 추적 | calendar, table |
| collect | 수집/기록 (책, 영화, 맛집) | gallery, table |
| manage | 프로젝트/태스크 관리 | board, timeline |
| plan | 계획/일정 (여행, 결혼) | calendar, table |
| organize | 정보 정리 (북마크, 연락처) | table, list |
| guide | 안내/온보딩/매뉴얼 | table, board |
| hub | 대시보드/팀 홈 | calendar, board |
| finance | 가계부/예산/투자 | table, calendar |
| journal | 일기/회고/감사 일지 | gallery, calendar |
| content | 콘텐츠 캘린더/SNS | board, calendar |
| learn | 학습/시험/어학 | table, board |
| crm | 고객 관리/영업 | board, timeline |

---

## 비용

| 항목 | 비용 |
|------|------|
| Notion API | 무료 |
| Gemini API (기본) | 무료 |
| Groq API (대안) | 무료 |
| Docker / uv / Vite | 무료 |
| **합계** | **$0** |

---

## 문서

| 문서 | 설명 |
|------|------|
| [변경 이력](docs/CHANGELOG.md) | 변경사항 + 회고 |
| [진행 현황](docs/CURRENT_STATUS.md) | 모듈별 진행률 |
| [스킬 가이드](docs/SKILL_GUIDE.md) | 스킬 작성 가이드 |
| [아키텍처](docs/ARCHITECTURE.md) | 시스템 설계 |
| [API 명세](docs/API.md) | REST/WebSocket 엔드포인트 |
| [블록 지원](docs/BLOCK_SUPPORT.md) | 74개 기능 상태 |

---

## 이어서 개발할 것 (TODO)

### 우선순위 HIGH
- [ ] AI 블록 다양성 강화 (quote, code, column_list 등 적극 활용)
- [ ] AI 모델 업그레이드 (Claude/GPT-4o = 더 복잡한 구조)

### 우선순위 MEDIUM — UI/UX
- [ ] 드래그 앤 드롭 블루프린트 재배치 (LivePreview에서 DB/서브페이지 순서 변경)
- [ ] 즐겨찾기 퀵 액세스 (사이드바에 starred 템플릿 바로가기)
- [ ] 블루프린트 JSON 내보내기/가져오기 (Export/Import 버튼)
- [ ] 실시간 연결 품질 모니터 (WebSocket ping/pong latency 실측)

### 우선순위 MEDIUM — 인프라
- [ ] Vercel (FE) + Railway (BE) 프로덕션 배포
- [ ] 스킬 간 크로스 조합 지원

### 우선순위 LOW
- [ ] 시연 영상 제작
- [ ] 가짜연구소 발표 자료
- [ ] 다국어 지원

---

## 라이선스

MIT License
