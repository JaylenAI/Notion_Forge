# 기술 아키텍처 (Architecture)

## 1. 시스템 개요

```
┌─────────────────────────────────────────────────────────┐
│                    사용자 (브라우저)                       │
│                    채팅 인터페이스                         │
└──────────────────────┬──────────────────────────────────┘
                       │ WebSocket / REST
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  Backend (FastAPI)                       │
│                                                         │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐ │
│  │ Chat API │→ │  AI Agent    │→ │ Notion Builder    │ │
│  │          │  │ (Claude API) │  │ (Notion API 호출) │ │
│  └──────────┘  └──────────────┘  └───────────────────┘ │
│                       │                    │            │
│                       ▼                    ▼            │
│              ┌──────────────┐    ┌─────────────────┐   │
│              │ Tool Router  │    │ Notion MCP      │   │
│              │ (도구 선택)   │    │ (보조 조회용)    │   │
│              └──────────────┘    └─────────────────┘   │
│                       │                                 │
│              ┌────────┼────────┐                        │
│              ▼        ▼        ▼                        │
│         ┌────────┐┌────────┐┌────────┐                  │
│         │create  ││create  ││add     │ ...              │
│         │page    ││database││blocks  │                  │
│         └────────┘└────────┘└────────┘                  │
└─────────────────────────────────────────────────────────┘
                       │
                       ▼ Notion API (https://api.notion.com/v1/)
┌─────────────────────────────────────────────────────────┐
│                 Notion Workspace                         │
│  생성된 페이지, 데이터베이스, 블록                         │
└─────────────────────────────────────────────────────────┘
```

---

## 2. 기술 스택

### Backend

| 기술 | 버전 | 용도 |
|------|------|------|
| **Python** | 3.11+ | 메인 언어 |
| **FastAPI** | 0.115+ | API 서버, WebSocket 지원 |
| **AI Providers** | 5종 | Copilot SDK / Claude / Gemini / Groq / OpenAI (Strategy Pattern) |
| **notion-client** | 2.x | Notion API Python SDK |
| **httpx** | 0.28+ | 비동기 HTTP 클라이언트 (듀얼 버전 API) |
| **Pydantic** | 2.x | 데이터 검증, 스키마 정의 |
| **uvicorn** | 0.32+ | ASGI 서버 |
| **uv** | 최신 | 패키지 관리 |

### Frontend

| 기술 | 버전 | 용도 |
|------|------|------|
| **React** | 19 | UI 프레임워크 |
| **Vite** | 7 | 빌드 도구 |
| **TailwindCSS** | 4 | 스타일링 |
| **Zustand** | 5 | 상태 관리 |

### 인프라 & 도구

| 기술 | 용도 |
|------|------|
| **Docker + Compose** | 개발/배포 컨테이너 환경 |
| **Claude Code** | 개발 환경 (AI 페어 프로그래밍) |
| **Notion MCP** | 노션 워크스페이스 조회 보조 |
| **GitHub Actions** | CI/CD |
| **Vercel** | 프론트엔드 배포 |
| **Railway** | 백엔드 배포 |

---

## 3. AI Agent 흐름

```
1. Input Guardrail — 프롬프트 인젝션 방어 + 입력 검증

2. 의도 분석 (Provider Strategy: Copilot/Claude/Gemini/Groq/OpenAI)
   → 템플릿 타입, 구성요소, 색상, 하위 페이지 파악

3. Skill Router (하이브리드)
   → 키워드 빠른경로 (score≥2) 또는 LLM 정밀 분류로 48개 스킬 중 선택

4. Episodic Memory
   → 과거 성공/실패 패턴 + 유저 선호도 → AI 컨텍스트 주입

5. 구조 설계 (JSON Blueprint) + Gen-Eval Loop (최대 3회)
   → 페이지 계층, DB 스키마, 블록 구성 생성 → 구조 검증 → 피드백 → 재생성
   → PostProcessor: 13종 자동 수정 (callout 보장, status 한글화, 샘플 보충 등)

6. 5-Pass Creation — Notion에 직접 생성
   → Pass 1: 메인 페이지 (아이콘/커버)
   → Pass 2: 서브페이지
   → Pass 3: 데이터베이스 (속성 + Relation) — legacy API 2022-06-28
   → Pass 4: 뷰 (10종 configuration) — 최신 API 2026-03-11
   → Pass 5: 샘플 데이터 (한국어 동의어 매핑)

7. 결과 반환 + Memory 저장
   → Notion 페이지 URL + 에피소드 기록 + 스킬 통계 갱신
   → 실패 시 자동 롤백 (생성된 리소스 삭제)
```

### Tool Registry (11개)

| Tool | 설명 |
|------|------|
| `create_page` | 페이지 생성 (커버, 아이콘, 제목) |
| `create_database` | DB 생성 + 속성 설정 |
| `add_blocks` | 블록 추가 (heading, callout, toggle, button 등) |
| `create_columns` | 칼럼 레이아웃 (2단/3단) |
| `add_database_items` | 샘플 데이터 입력 (한국어 동의어 매핑) |
| `create_view` | DB 뷰 생성 (gallery, board, calendar 등 10종) |
| `apply_color_theme` | 색상 테마 일괄 적용 |
| `link_databases` | DB 간 Relation/Rollup 설정 |
| `generate_cover` | 커버 이미지 URL 생성 |
| `create_worker` | Notion Workers 생성 (Sync/Tool/Webhook) |
| `register_agent` | External Agent Notion 등록 |

---

## 4. 데이터 모델: Template Blueprint

AI가 생성하는 중간 구조 (JSON):

```json
{
  "template": {
    "title": "프로젝트 대시보드",
    "icon": "🏢",
    "cover": { "type": "url", "url": "https://images.unsplash.com/..." },
    "color_theme": "orange",
    "layout": {
      "type": "columns",
      "columns": [
        {
          "width": "30%",
          "blocks": [
            { "type": "calendar_db_link", "ref": "main_db" },
            { "type": "nav_section", "links": ["ETC", "Project", "Study"] }
          ]
        },
        {
          "width": "70%",
          "blocks": [
            { "type": "heading_1", "text": "Project", "color": "orange_background" },
            { "type": "database_view", "ref": "main_db", "view": "gallery" }
          ]
        }
      ]
    },
    "databases": [
      {
        "id": "main_db",
        "title": "Projects",
        "properties": {
          "이름": { "type": "title" },
          "카테고리": { "type": "select", "options": ["LLM", "Web", "Mobile"] },
          "상태": { "type": "status" },
          "날짜": { "type": "date" }
        }
      }
    ],
    "sub_pages": [
      { "title": "ETC", "icon": "🎪", "layout": {} }
    ]
  }
}
```

---

## 5. Notion API 상세

### API 기본 정보

| 항목 | 값 |
|------|-----|
| API 버전 (읽기/뷰/Workers) | `2026-03-11` |
| API 버전 (DB/페이지 생성) | `2022-06-28` (속성 정상 처리를 위한 legacy) |
| Base URL | `https://api.notion.com/v1/` |
| 인증 | Internal Integration Token (`ntn_xxxx`) |
| Rate Limit | **3 req/s** (평균) |
| 블록 추가 | max **100 blocks/request** |
| Rich Text | max 2000자/블록 |
| 비용 | **무료** |

> **듀얼 버전 전략**: `2026-03-11`은 DB 생성 시 properties를 무시하고 200 OK를 반환하는 문제가 있음.
> DB/페이지 생성·수정·아이템 추가는 `_http_client_legacy` (2022-06-28)를 사용하고,
> Views/Workers/Data Sources/쿼리는 `_http_client` (2026-03-11)를 사용.

### 블록 타입별 지원 현황

**텍스트/콘텐츠:**

| 블록 타입 | API 생성 | 색상 지정 | 활용 |
|-----------|---------|----------|------|
| `paragraph` | ✅ | ✅ text/bg | 본문 텍스트 |
| `heading_1/2/3` | ✅ | ✅ text/bg | 제목 |
| `callout` | ✅ | ✅ bg | 안내/강조 박스 |
| `quote` | ✅ | ✅ text/bg | 인용 |
| `toggle` | ✅ | ✅ text/bg | FAQ, 접기/펼치기 |
| `code` | ✅ | ❌ | 코드 블록 |
| `divider` | ✅ | ❌ | 구분선 |

**목록:**

| 블록 타입 | API 생성 | 활용 |
|-----------|---------|------|
| `bulleted_list_item` | ✅ | 일반 목록 |
| `numbered_list_item` | ✅ | 번호 목록 |
| `to_do` | ✅ | 체크리스트 |

**레이아웃:**

| 블록 타입 | API 생성 | 활용 |
|-----------|---------|------|
| `column_list` / `column` | ✅ | 2단/3단 레이아웃 |
| `table` / `table_row` | ✅ | 정적 테이블 |

**미디어/DB:**

| 블록 타입 | API 생성 | 활용 |
|-----------|---------|------|
| `image` / `bookmark` / `embed` | ✅ | 미디어 |
| `child_database` | ✅ | **인라인 DB (핵심)** |
| `child_page` / `link_to_page` | ✅ | 중첩/네비게이션 |
| `table_of_contents` / `breadcrumb` | ✅ | 보조 |

**2026년 3월 신규:**

| 블록 타입 | API 생성 | 활용 |
|-----------|---------|------|
| `tab` | ✅ (2026-03-25) | 탭으로 콘텐츠 구분 |
| `synced_block` | ✅ (원본만) | 동기화 블록 원본 생성 |

**미지원:**

| 블록 | 대안 |
|------|------|
| `button` | ✅ 지원 (v8.0.0) — 자동화 트리거 |
| `link_preview` | bookmark으로 대체 |

### Views API (2026-03-19 신규) — 10개 뷰 전부 동작 확인

DB 뷰를 API로 생성/수정/삭제 가능. **실제 테스트 완료:**

| 뷰 타입 | 생성 | 테스트 결과 |
|---------|------|-----------|
| table (표) | ✅ | 기본 뷰 |
| board (칸반) | ✅ | 동작 확인 |
| calendar (캘린더) | ✅ | 동작 확인 |
| timeline (타임라인) | ✅ | 동작 확인 |
| gallery (갤러리) | ✅ | 동작 확인 |
| list (리스트) | ✅ | 동작 확인 |
| chart (차트) | ✅ | 동작 확인 |
| form (폼) | ✅ | 동작 확인 |
| map (지도) | ✅ | 동작 확인 |
| dashboard (대시보드) | ✅ | 동작 확인 |

**핵심**: `data_source_id ≠ database_id`. DB 생성 후 `get_database()` → `data_sources[0].id` 추출 필수.

### DB 속성 타입

| 속성 타입 | 지원 | 예시 |
|-----------|------|------|
| `title` | ✅ (필수) | DB 항목 이름 |
| `rich_text` / `number` | ✅ | 메모, 평점 |
| `select` / `multi_select` | ✅ **자주 사용** | 카테고리, 태그 (색상 옵션) |
| `date` / `checkbox` | ✅ | 날짜, 즐겨찾기 |
| `url` / `email` / `phone_number` | ✅ | 링크, 연락처 |
| `status` | ✅ | 시작전/진행중/완료 |
| `relation` / `rollup` | ✅ | DB 간 연결, 집계 |
| `formula` | ⚠️ | 기본 수식만 |
| `people` / `files` | ⚠️ | 멤버/URL만 |
| `unique_id` / `created_time` / `last_edited_time` | ✅ | 자동 |

Select 옵션 색상: `default`, `gray`, `brown`, `orange`, `yellow`, `green`, `blue`, `purple`, `pink`, `red`

### Rate Limit 대응 전략

```
1. Semaphore 기반 동시 요청 제한 (max_per_second 슬롯)
2. 지수 백오프 (429 → 0.5초 → 1초 → 2초)
3. 병렬 실행 (서브페이지, 뷰, 블록 채우기는 asyncio.gather)
4. 사전 블록 구성 후 한번에 호출 (100개/요청)
```

| 템플릿 유형 | API 호출 | 소요 시간 |
|------------|---------|----------|
| 단일 페이지 (DB 1개) | ~5-8회 | 3-5초 |
| 대시보드 (DB 2개 + 칼럼) | ~10-15회 | 5-8초 |
| 다중 페이지 (하위 3개) | ~20-30회 | 10-15초 |
| 복잡한 워크스페이스 | ~40-60회 | 20-30초 |

### 알려진 제한 및 해결

| 제한 | 해결 |
|------|------|
| 2026-03-11에서 DB 속성 무시 | 듀얼 버전: DB 생성은 2022-06-28 사용 |
| Button 블록 미지원 | 콜아웃 + emoji + 링크 |
| 블록 위치 삽입 불가 (append만) | 순서 미리 정해서 순서대로 append |
| Rich Text 2000자 제한 | 여러 블록으로 분할 |
| 중첩 2단계 제한 | 구조 설계 시 깊이 제한 |

---

## 6. Provider 안정성

### Retry + Exponential Backoff

```
call_with_retry(prompt, message, max_retries=2, timeout=45s)
  → 시도 1: 호출
  → transient 에러 (429, 503, timeout): 0.5s 대기 후 재시도
  → 시도 2: 호출
  → transient 에러: 1.0s 대기 후 재시도
  → 시도 3: 실패 → None 반환
  → permanent 에러 (401, 403): 즉시 None 반환 (재시도 없음)
```

### Circuit Breaker

```
CircuitBreaker(threshold=3, reset_seconds=120)
  → 연속 3회 실패 → circuit OPEN (프로바이더 차단)
  → 120초 후 자동 HALF-OPEN (1회 시도 허용)
  → 성공 시 → circuit CLOSED (정상 복귀)
```

### Provider Fallback Chain

```
resolve_with_fallback(api_key)
  → primary 프로바이더 확인
  → circuit OPEN? → fallback chain 탐색 (openai → claude → gemini → groq)
  → 건강한 프로바이더 반환
  → 모든 프로바이더 차단? → 전체 리셋 후 primary 강제 사용
```

### 프리미엄 DB 기능

| 기능 | 설명 | 후처리 |
|------|------|--------|
| Relation | DB 간 연결 (target_db_index → 실제 DB ID) | post_process_relations |
| Formula | 계산 필드 (D-Day, 진행률 등) | post_process_relations |
| Rollup | 관계 DB 집계 (sum, count, average) | post_process_relations |
| LinkedView | 다른 페이지에 필터링된 DB 뷰 삽입 | execute_streaming |

---

## 7. Notion MCP 활용

```
Notion MCP (조회/보조):
├─ 기존 워크스페이스 구조 조회
├─ 사용자의 기존 DB 스키마 참고
└─ 생성된 결과 검증

Notion API 직접 호출 (생성/핵심):
├─ 페이지, DB, 블록 생성
└─ 모든 쓰기 작업
```

MCP 서버 설정:
```json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": {
        "OPENAPI_MCP_HEADERS": "{\"Authorization\": \"Bearer ntn_xxx\", \"Notion-Version\": \"2022-06-28\"}"
      }
    }
  }
}
```

---

## 8. 프로젝트 디렉토리 구조

```
NotionForge/
├── README.md
├── .env.example
├── docker-compose.yml             # Docker 환경
├── docs/                          # 문서 (10개)
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── main.py                    # FastAPI 진입점
│   ├── config.py                  # 환경변수, 설정
│   ├── agent/
│   │   ├── orchestrator.py        # Agent 오케스트레이터
│   │   ├── intent_analyzer.py     # 의도 분석 (AI Provider)
│   │   ├── blueprint_generator.py # 구조 설계 + Gen-Eval 루프
│   │   ├── agent_loop.py          # Plan-Execute-Reflect 루프
│   │   ├── skill_router.py        # 하이브리드 스킬 라우터 (키워드+LLM)
│   │   ├── memory.py              # Episodic Memory (학습)
│   │   ├── providers/             # 6개 AI 프로바이더 Strategy 패턴
│   │   │   ├── base.py / router.py
│   │   │   ├── copilot_provider.py / claude_provider.py
│   │   │   ├── gemini_provider.py / groq_provider.py
│   │   │   └── openai_provider.py / mock_provider.py
│   │   └── tools/                 # 9개 Tool (+ create_view)
│   │       ├── base.py / registry.py
│   │       ├── create_page.py / create_database.py
│   │       ├── add_blocks.py / add_database_items.py
│   │       ├── create_columns.py / create_view.py
│   │       ├── apply_color_theme.py
│   │       ├── link_databases.py
│   │       └── generate_cover.py
│   ├── notion/
│   │   ├── client.py              # API 클라이언트 래퍼
│   │   ├── rate_limiter.py        # Rate limit
│   │   └── block_builder.py       # 블록 JSON 빌더
│   ├── patterns/                  # 템플릿 패턴 라이브러리
│   ├── routers/
│   │   ├── chat.py                # WebSocket 채팅
│   │   ├── template.py            # REST API
│   │   ├── ai.py                  # AI 모델/프로바이더 API
│   │   ├── workspace.py           # 워크스페이스 + Memory API
│   │   ├── recipes.py             # 커뮤니티 레시피 API
│   │   ├── oauth.py               # Notion OAuth 연동
│   │   └── skills.py              # 커스텀 스킬 CRUD
│   └── tests/
├── frontend/
│   ├── package.json
│   └── src/
│       ├── App.tsx
│       ├── components/            # Chat, Preview, Progress
│       ├── stores/                # Zustand
│       └── api/                   # API 클라이언트
└── .github/workflows/ci.yml
```
