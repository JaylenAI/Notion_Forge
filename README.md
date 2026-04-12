# NotionForge

> AI 채팅으로 노션 템플릿을 자동 생성하는 오픈소스 에이전트

## 프로젝트 개요

**NotionForge**는 사용자가 자연어로 원하는 노션 템플릿을 설명하면, AI Agent가 Notion API를 통해 완성된 템플릿을 자동으로 생성해주는 서비스입니다.

> **소속**: 가짜연구소 - "나만의 자동화 AI Agent 만들기" 프로젝트
> **브랜치**: `copilot-sdk` (v7.0.0 — 하네스 엔지니어링 + Copilot SDK, 최신) | `dev-2` (v6.x)

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
git checkout copilot-sdk    # v7.0.0 하네스 엔지니어링 (최신)
cp .env.example .env
```

### 2단계: .env 설정

```env
# 필수 (2개만 설정하면 됩니다)
NOTION_API_KEY=ntn_xxxx          # https://notion.so/my-integrations
NOTION_PARENT_PAGE_ID=xxxxx      # 템플릿 생성할 부모 페이지 ID

# AI 프로바이더 (우선순위: Copilot > Claude > Gemini > Groq > Mock)
# GitHub Copilot 구독자: 아무것도 안 해도 자동 활성화 (API 키 불필요!)
COPILOT_ENABLED=true             # Copilot SDK (GPT-4.1 등 7개 모델, 무료)
ANTHROPIC_API_KEY=               # Claude API (유료, 최고 품질)
GEMINI_API_KEY=                  # Gemini API (무료, 일 20회)
GROQ_API_KEY=gsk_xxxx            # Groq API (무료, 빠름)
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
- **프로 디자인 품질**: Thomas Frank/Easlo 수준 디자인 규칙 (2-3색 팔레트, 3컬럼 대시보드, 정보 계층)
- **복잡도 스케일링**: 간단(10블록) → 중간(20블록) → 복잡(40블록+, 3-4 DB, 서브페이지 5+) 자동 조절
- **12개 스킬**: track, collect, manage, plan, organize, guide, hub, finance, journal, content, learn, crm
- **5개 AI 프로바이더**: Copilot SDK (GPT-4.1 등 7개, 무료) / Claude / Gemini / Groq / OpenAI
- **실시간 스트리밍**: 생성 과정을 단계별로 표시 (의도 분석 → 설계 → 페이지 → DB → 뷰 → 완료)
- **스마트 폴백**: AI 실패 시 키워드 기반 6개 템플릿 자동 선택
- **멀티턴 대화형 수정**: 생성 후 "속성 추가해줘", "뷰 바꿔줘", "DB 연결해줘" 등 자연어로 수정
- **Relation/Rollup/Formula**: DB 간 관계 자동 연결 + 수식 자동 생성 (D-Day, 진행률 등)
- **멀티 에이전트 파이프라인**: Architect→Designer→Content→Validator 4단계 (고급 모드)
- **Document-to-Notion**: CSV/MD/TXT/PDF 업로드 → 자동 템플릿 변환
- **커뮤니티 레시피**: recipes/ 디렉토리에서 JSON 레시피 공유 + 원클릭 생성
- **다국어 지원**: 한국어/영어/일본어 선택 가능
- **OAuth 연동**: Notion OAuth 플로우 (토큰 복붙 대신 원클릭 연결)
- **커스텀 스킬**: 유저가 직접 스킬 추가 → 맞춤형 AI Agent 구축 (시스템 프롬프트 커스터마이징)

### Notion API 전체 지원 (74개 기능 + 확장)
- **블록 30+종**: heading, callout, toggle, quote, code, table, equation, tab, synced_block 등
- **인라인 서식**: bold, italic, underline, strikethrough, code, link, 색상, 멘션
- **미디어**: image, video, audio, file, pdf, bookmark, embed (Figma, GitHub, Loom 등 12개)
- **DB 뷰 10개**: table, gallery, calendar, board, timeline, list, chart, form, map, dashboard
- **DB 속성 전체**: select, multi_select, status, relation, rollup, formula, unique_id, people 등
- **컬럼 너비 비율**: width_ratio로 30/70 대시보드 분할 지원
- **페이지 전체 너비**: Internal API로 자동 전체 너비 설정 (token_v2 옵션)
- **링크드 DB 뷰**: Views API로 기존 DB를 다른 페이지에 링크드 뷰로 삽입
- **블록 position 제어**: 특정 블록 뒤에 삽입, 서브페이지 하단 배치
- **미리보기=실제 일치**: 프리뷰에서 보이는 그대로 Notion에 생성
- **DB 고도화**: description, icon, cover 지원
- **뷰 고도화**: group_by, quick_filters, 속성 표시/숨김, 위치 제어
- **블록/스레드 코멘트**: 블록 레벨 댓글 + 답글 스레드
- **페이지 이동**: 페이지 부모 변경 API
- **링크드 DB뷰**: 같은 DB를 다른 필터로 대시보드 위젯 표시

### 프론트엔드
- **다크/라이트 테마**: CSS 변수 기반 전체 테마 시스템 + 토글
- **5개 페이지**: Dashboard, Library, Integrations, Profile, Support
- **프롬프트 스타터**: 6개 추천 템플릿 원클릭 생성
- **프롬프트 라이브러리**: 4개 카테고리 × 18개 프롬프트 템플릿 (Business/Personal/Content/Learning)
- **노션 스타일 렌더러**: 14개 블록 + 4개 DB 뷰 (Table/Board/Calendar/Gallery) 미리보기
- **Library 수동 저장**: Save to Library 버튼으로 원하는 템플릿만 보관 + 검색/필터/정렬
- **AI 모델 선택**: 프로바이더 자동 감지 + 모델 목록 API
- **채팅 마크다운 렌더링**: AI 응답에 bold, 리스트, 코드블록, 테이블 등 렌더링
- **채팅 세션 관리**: 세션 자동저장/복원/삭제, 최대 50개 히스토리
- **키보드 단축키**: ⌘N 새 템플릿, ⌘K 커맨드 팔레트
- **미리보기 줌**: 50%~150% 줌 인/아웃
- **모바일 반응형**: 768px 이하 탭 전환 UI, 오버레이 사이드바
- **토스트 알림**: 저장/연결/에러 시 피드백
- **생성 취소**: 진행 중인 템플릿 생성 취소 가능
- **실시간 생성 로그**: 생성 과정을 채팅에서 실시간 스트리밍

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
│   │   │   ├── orchestrator.py    # 실시간 스트리밍 파이프라인 + 멀티턴 수정
│   │   │   ├── intent_analyzer.py # 의도 분석 (4개 프로바이더)
│   │   │   ├── blueprint_generator.py  # Gen-Eval 피드백 루프 + AI 설계
│   │   │   ├── prompt_assembler.py    # 동적 프롬프트 조립 (모듈 .md)
│   │   │   ├── layout_router.py       # 의도→8개 레이아웃 자동 매핑
│   │   │   ├── post_processor.py      # AI 출력 검증 + 자동 보정
│   │   │   ├── pipeline.py        # 멀티 에이전트 파이프라인
│   │   │   ├── document_parser.py # Document-to-Notion (CSV/MD/PDF)
│   │   │   ├── prompts/           # 모듈화된 프롬프트 (.md)
│   │   │   │   ├── base.md / views_catalog.md / relations.md
│   │   │   │   ├── modes/         # simple / standard / advanced
│   │   │   │   └── layouts/       # 8개 레이아웃 패턴
│   │   │   └── tools/             # 8개 Tool
│   │   ├── routers/
│   │   │   ├── chat.py            # WebSocket 채팅
│   │   │   ├── template.py        # REST API + Blueprint Import
│   │   │   ├── recipes.py         # 커뮤니티 레시피 API
│   │   │   ├── oauth.py           # Notion OAuth 연동
│   │   │   └── skills.py          # 커스텀 스킬 CRUD API
│   │   ├── notion/                # Notion API 클라이언트 (74개 기능)
│   │   ├── skills/                # 12개 스킬 (.md)
│   │   │   ├── track/   collect/   manage/   plan/
│   │   │   ├── organize/ guide/    hub/
│   │   │   ├── finance/  journal/  content/
│   │   │   └── learn/    crm/
│   │   ├── routers/               # REST + WebSocket
│   │   └── schemas/
│   └── tests/                     # 71개 테스트 (100% 통과)
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
| **AI** | Copilot SDK (GPT-4.1, 기본) / Claude / Gemini / Groq / OpenAI |
| **Notion** | notion-client 3.x + httpx (Legacy 2022-06-28 + Views 2025-09-03 + Internal API) |
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
| Copilot SDK (GPT-4.1, 기본) | 무료 (GitHub Copilot 구독 필요) |
| Gemini API (대안) | 무료 (일 20회) |
| Groq API (대안) | 무료 |
| Docker / uv / Vite | 무료 |
| **합계** | **$0** (Copilot 구독 시) |

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

## 하네스 엔지니어링 아키텍처 (v7.0.0)

AI 모델은 범용 도구일 뿐, **하네스(harness)가 결과 품질을 결정합니다.**

```
유저 입력: "CRM 대시보드 만들어줘"
    |
[1. Intent Analyzer] — 의도 분석 (CREATE / MODIFY / QUESTION)
    |
[2. Mode Detector] — 복잡도 자동 감지 (simple / standard / advanced)
    |
[3. Layout Router] — 8개 레이아웃 중 최적 선택 (→ dashboard_widgets)
    |
[4. Prompt Assembler] — 모듈 .md 동적 조립
    |   base.md + modes/advanced.md + layouts/dashboard_widgets.md + views_catalog.md + ...
    |
[5. AI Generation] — Copilot(GPT-4.1) / Claude / Gemini / Groq
    |
[6. Gen-Eval Loop] — 구조적 검증 → 실패 시 에러를 AI에게 피드백 → 재생성 (최대 3회)
    |   Level 0: 필수 필드 존재
    |   Level 1: 블록 구조 (db_ref 위치, 타입)
    |   Level 2: DB 구조 (title 속성, sample_items)
    |   Level 3: 참조 범위 (db_index 유효성)
    |
[7. Post-Processor] — 자동 보정 (callout 누락 추가, status 한국어 매핑, spacing)
    |
[8. Notion Creation] — 실제 Notion API 호출 (페이지 → 서브페이지 → DB → 뷰 → 블록)
```

### 8개 레이아웃 패턴

| 레이아웃 | 용도 | 기본 뷰 |
|---------|------|---------|
| `simple_tracker` | 물/운동/습관/수면 트래커 | table |
| `gallery_hero` | 일기/독서/레시피 컬렉션 | gallery |
| `kanban_board` | 프로젝트/태스크/스프린트 | board |
| `calendar_main` | 일정/콘텐츠 캘린더 | calendar |
| `dashboard_widgets` | CRM/대시보드/KPI | board + chart |
| `category_hub` | 온보딩/위키/가이드 | toggles |
| `portfolio` | 포트폴리오/이력서 | gallery + timeline |
| `sidebar_main` | 범용 (기본값) | table |

---

## 이어서 개발할 것 (TODO)

### v6.0.0 완료 (2026-04-08)
- [x] Relation + Rollup + Formula 자동 생성
- [x] 멀티턴 대화형 수정 (속성/뷰/DB/Relation/Formula/서브페이지/블록)
- [x] 복잡도/언어 선택 UI (Simple/Standard/Advanced + KR/EN/JP)
- [x] Blueprint JSON Export/Import
- [x] 커뮤니티 레시피 갤러리 (recipes/ + API + UI)
- [x] 다국어 지원 (한/영/일)
- [x] 멀티 에이전트 파이프라인 (Architect→Designer→Content→Validator)
- [x] Document-to-Notion (CSV/MD/TXT/PDF)
- [x] OAuth 연동 (Notion OAuth 플로우)
- [x] 디자인 토큰 시스템 (카테고리별 통일)
- [x] 혼합 리치텍스트 (bold+color 복합 서식)
- [x] 서브페이지 AI 블록 패스스루 수정

### v7.0.0 완료 (2026-04-10) — 하네스 엔지니어링
- [x] Copilot SDK 연동 (GPT-4.1 등 7개 모델, API 키 불필요)
- [x] 프롬프트 모듈화 (prompts/*.md 동적 조립)
- [x] Intent Router (8개 레이아웃 자동 매핑)
- [x] 레이아웃 프롬프트 8종 (각각 고유한 블록 배치)
- [x] Gen-Eval 피드백 루프 (검증 실패 → AI에게 에러 피드백 → 재생성, 최대 3회)
- [x] Post-processor 검증 레이어 (7개 규칙 자동 보정)
- [x] Circuit Breaker (최대 재시도 초과 시 최선 결과 사용)
- [x] Copilot 모델 선택 UI (프론트엔드 Integrations 페이지)
- [x] 테스트 71/71 통과 (하네스 32개 포함)

### v7.1.0 완료 (2026-04-12) — 하네스 고도화 + 프로 템플릿 품질
- [x] Nesting 패턴: callout/toggle/heading children 사용법 + JSON 예시 (base.md)
- [x] 레이아웃 8종에 완성된 JSON blocks[] 예시 추가
- [x] 스킬 12개 핵심 패턴 추출 (15줄 잘림 → 핵심 섹션 자동 추출)
- [x] link_to_page 동적 주입: `sub_page_ref` 플레이스홀더 → ID 치환
- [x] DB 배치 전략: `db_parent` 필드로 서브페이지에 DB 생성 + 메인에 linked_view
- [x] 2-Stage 파이프라인: advanced 모드에서 자동 활성화 (Architect→Designer→Content→Validator)
- [x] Model Escalation: GPT-4.1 실패 → GPT-5.2 → GPT-5 Mini 자동 업그레이드

### 다음 개발 예정 (v8.0.0)

- [ ] Human-in-the-Loop: "DB 3개 생성합니다. 진행할까요?" 승인 게이트
- [ ] Observability 대시보드: 토큰 비용, 재시도 횟수, 소요시간 시각화

**기타:**
- [ ] Vercel (FE) + Railway (BE) 프로덕션 배포
- [ ] 시연 영상 + 발표 자료

---

## 라이선스

MIT License
