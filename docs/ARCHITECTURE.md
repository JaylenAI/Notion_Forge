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
| **FastAPI** | 0.110+ | API 서버, WebSocket 지원 |
| **Claude API** | claude-sonnet-4-6 | AI 의도 분석, 구조 설계 |
| **notion-client** | 2.x | Notion API Python SDK |
| **Pydantic** | 2.x | 데이터 검증, 스키마 정의 |
| **uvicorn** | 0.30+ | ASGI 서버 |
| **httpx** | 0.27+ | 비동기 HTTP 클라이언트 |
| **uv** | 최신 | 패키지 관리 (Poetry 대체) |

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
1. 사용자 입력 수신
   "프로젝트 관리 대시보드 만들어줘, 갤러리 뷰, 주황색 톤, 하위 페이지 3개"

2. 의도 분석 (Claude API)
   → 템플릿 타입, 구성요소, 색상, 하위 페이지 파악

3. 구조 설계 (JSON Blueprint)
   → 페이지 계층, DB 스키마, 블록 구성 생성

4. Tool 선택 & 실행
   → 필요한 Tool을 순서대로 호출하여 Notion API 실행

5. 결과 반환
   → 생성된 Notion 페이지 URL + 요약 정보
```

### Tool 정의 (8개)

| Tool | 설명 |
|------|------|
| `create_page` | 페이지 생성 (커버, 아이콘, 제목) |
| `create_database` | DB 생성 + 속성 설정 |
| `add_blocks` | 블록 추가 (heading, callout, toggle 등) |
| `create_columns` | 칼럼 레이아웃 (2단/3단) |
| `add_database_items` | 샘플 데이터 입력 |
| `apply_color_theme` | 색상 테마 일괄 적용 |
| `link_databases` | DB 간 Relation/Rollup 설정 |
| `generate_cover` | 커버 이미지 URL 생성 |

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
| API 버전 | `2022-06-28` |
| Base URL | `https://api.notion.com/v1/` |
| 인증 | Internal Integration Token (`ntn_xxxx`) |
| Rate Limit | **3 req/s** (평균) |
| 블록 추가 | max **100 blocks/request** |
| Rich Text | max 2000자/블록 |
| 비용 | **무료** |

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
| `button` | 콜아웃 + 링크 블록 |
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

```python
# 1. 블록 배치 처리 (100개씩)
# 2. 지수 백오프 (429 → 1초 → 2초 → 4초)
# 3. 요청 큐 (3req/s 준수)
# 4. 사전 블록 구성 후 한번에 호출
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
| DB 뷰 커스텀 불가 | 기본 뷰 생성, 뷰 변경 안내 |
| Button 블록 미지원 | 콜아웃 + emoji + 링크 |
| 블록 위치 삽입 불가 (append만) | 순서 미리 정해서 순서대로 append |
| Rich Text 2000자 제한 | 여러 블록으로 분할 |
| 중첩 2단계 제한 | 구조 설계 시 깊이 제한 |

---

## 6. Notion MCP 활용

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

## 7. 프로젝트 디렉토리 구조

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
│   │   ├── intent_analyzer.py     # 의도 분석 (Claude API)
│   │   ├── blueprint_generator.py # 구조 설계
│   │   └── tools/                 # 8개 Tool
│   │       ├── base.py
│   │       ├── create_page.py
│   │       ├── create_database.py
│   │       ├── add_blocks.py
│   │       ├── add_database_items.py
│   │       ├── create_columns.py
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
│   │   └── template.py            # REST API
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
