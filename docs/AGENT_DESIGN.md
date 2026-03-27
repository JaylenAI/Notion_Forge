# AI Agent 설계 (Agent Design)

> NotionForge의 핵심: AI Agent가 사용자 의도를 분석하고 Tool을 선택해 Notion 템플릿을 생성하는 구조

---

## 1. Agent 아키텍처

### 전체 구조

```
┌─────────────────────────────────────────────┐
│              Agent Orchestrator              │
│                                             │
│  ┌─────────────┐    ┌──────────────────┐   │
│  │   Intent     │    │    Blueprint     │   │
│  │  Analyzer    │───→│   Generator     │   │
│  │ (의도 분석)   │    │  (구조 설계)     │   │
│  └─────────────┘    └───────┬──────────┘   │
│                             │              │
│                      ┌──────▼──────┐       │
│                      │ Tool Router │       │
│                      │ (도구 선택)  │       │
│                      └──────┬──────┘       │
│                             │              │
│              ┌──────────────┼──────────┐   │
│              ▼              ▼          ▼   │
│         ┌────────┐   ┌──────────┐ ┌──────┐│
│         │ Page   │   │ Database │ │Block ││
│         │ Tools  │   │  Tools   │ │Tools ││
│         └────────┘   └──────────┘ └──────┘│
└─────────────────────────────────────────────┘
```

### 처리 파이프라인

```
Step 1: Intent Analysis (의도 분석)
  └─ 사용자 메시지 → Claude API → 구조화된 의도 (JSON)

Step 2: Blueprint Generation (구조 설계)
  └─ 의도 + 패턴 라이브러리 → Claude API → Template Blueprint (JSON)

Step 3: Tool Execution (도구 실행)
  └─ Blueprint → Tool 순서 결정 → Notion API 호출 → 결과 수집

Step 4: Validation (검증)
  └─ 생성 결과 확인 → 에러 시 재시도 → 완료 URL 반환
```

---

## 2. Intent Analyzer (의도 분석기)

### Claude API 프롬프트 (System)

```
당신은 Notion 템플릿 생성 전문가입니다.
사용자의 자연어 요청을 분석하여 아래 JSON 형식으로 구조화하세요.

분석 결과:
{
  "intent": "CREATE | MODIFY | QUESTION | CONFIRM | REJECT",
  "template_type": "dashboard | tracker | bookmark | project | note | crm | onboarding | custom",
  "title": "템플릿 제목 (사용자가 명시하지 않으면 적절히 생성)",
  "color_theme": "blue | orange | green | red | purple | pink | yellow | gray | default",
  "layout": "single | two_column | three_column",
  "databases": [
    {
      "name": "DB 이름",
      "purpose": "DB 용도",
      "properties": ["속성1: 타입", "속성2: 타입"],
      "view_type": "gallery | table | board | calendar | list"
    }
  ],
  "sub_pages": ["하위 페이지1", "하위 페이지2"],
  "special_features": ["즐겨찾기 필터", "칼럼 레이아웃", "샘플 데이터"],
  "missing_info": ["부족한 정보 (AI가 추가 질문할 내용)"],
  "confidence": 0.85
}

규칙:
- 사용자가 정보를 충분히 제공하지 않으면 missing_info에 질문 목록 추가
- confidence가 0.7 미만이면 반드시 확인 질문
- 색상은 한국어도 매핑: "하늘색" → "blue", "주황색" → "orange"
- 템플릿 타입을 명확히 판단할 수 없으면 "custom"
```

### 의도 분류 예시

| 사용자 입력 | intent | template_type | confidence |
|------------|--------|---------------|-----------|
| "프로젝트 관리 대시보드 만들어줘" | CREATE | dashboard | 0.95 |
| "습관 트래커 좀" | CREATE | tracker | 0.90 |
| "노션 만들어줘" | CREATE | custom | 0.30 (질문 필요) |
| "DB에 태그 속성 추가해줘" | MODIFY | - | 0.85 |
| "버튼 넣을 수 있어?" | QUESTION | - | 0.90 |

---

## 3. Blueprint Generator (구조 설계기)

### 패턴 라이브러리 활용

의도 분석 결과의 `template_type`에 따라 사전 정의된 패턴을 기반으로 Blueprint 생성:

```python
PATTERN_LIBRARY = {
    "dashboard": {
        "layout": "two_column",
        "left_ratio": 30,
        "left_components": ["calendar", "nav_links"],
        "right_components": ["heading", "database_gallery"],
        "default_db_properties": ["이름", "카테고리:select", "상태:status", "날짜:date"],
        "sub_pages": True,
    },
    "tracker": {
        "layout": "single",
        "components": ["heading", "stats_callout", "database_table"],
        "default_db_properties": ["항목", "완료:checkbox", "날짜:date", "메모:rich_text"],
        "sub_pages": False,
    },
    "bookmark": {
        "layout": "two_column",
        "left_ratio": 30,
        "left_components": ["category_list"],
        "right_components": ["guide_callout", "database_gallery"],
        "default_db_properties": ["이름", "URL:url", "카테고리:select", "즐겨찾기:checkbox"],
        "sub_pages": False,
    },
    "note": {
        "layout": "two_column",
        "left_ratio": 25,
        "left_components": ["quick_actions", "menu_links"],
        "right_components": ["guide_toggle", "database_gallery"],
        "default_db_properties": ["이름", "종류:select", "평점:number", "즐겨찾기:checkbox", "날짜:date"],
        "sub_pages": True,
    },
    "onboarding": {
        "layout": "single",
        "components": ["welcome_callout", "weekly_checklists", "department_columns", "handover_db", "faq_toggles"],
        "default_db_properties": ["항목", "담당자:people", "상태:status", "기한:date"],
        "sub_pages": True,
    },
}
```

### Blueprint JSON 구조

```json
{
  "version": "1.0",
  "metadata": {
    "title": "프로젝트 대시보드",
    "template_type": "dashboard",
    "color_theme": "orange",
    "created_by": "NotionForge",
    "estimated_api_calls": 25
  },
  "pages": [
    {
      "id": "main",
      "title": "프로젝트 대시보드",
      "icon": { "type": "emoji", "emoji": "🏢" },
      "cover": { "type": "external", "url": "..." },
      "children": [
        {
          "type": "column_list",
          "columns": [
            {
              "ratio": 30,
              "children": [
                { "type": "linked_database", "ref": "main_db", "view": "calendar" },
                { "type": "heading_2", "text": "ETC", "color": "orange_background" },
                { "type": "page_link", "ref": "sub_etc" }
              ]
            },
            {
              "ratio": 70,
              "children": [
                { "type": "heading_1", "text": "Project", "color": "orange_background" },
                { "type": "child_database", "ref": "main_db" }
              ]
            }
          ]
        }
      ]
    },
    {
      "id": "sub_etc",
      "title": "ETC",
      "icon": { "type": "emoji", "emoji": "🎪" },
      "parent": "main",
      "children": [ "..." ]
    }
  ],
  "databases": [
    {
      "id": "main_db",
      "title": "Projects",
      "is_inline": true,
      "properties": {
        "이름": { "type": "title" },
        "카테고리": {
          "type": "select",
          "options": [
            { "name": "LLM", "color": "purple" },
            { "name": "Web", "color": "blue" },
            { "name": "Mobile", "color": "green" },
            { "name": "Data", "color": "orange" }
          ]
        },
        "상태": { "type": "status" },
        "날짜": { "type": "date" }
      },
      "sample_items": [
        {
          "이름": "LLM Model Comparison",
          "카테고리": "LLM",
          "icon": "🐱",
          "cover_url": "..."
        }
      ]
    }
  ]
}
```

---

## 4. Tools 정의 (Agent가 사용하는 도구)

### Tool 목록

| # | Tool | 설명 | 입력 | 출력 |
|---|------|------|------|------|
| 1 | `create_page` | 노션 페이지 생성 | title, icon, cover, parent_id | page_id, url |
| 2 | `create_database` | DB 생성 + 속성 설정 | title, properties, parent_id, is_inline | database_id |
| 3 | `add_blocks` | 블록 추가 | page_id, blocks[] | block_ids[] |
| 4 | `create_columns` | 칼럼 레이아웃 생성 | page_id, columns[] | column_ids[] |
| 5 | `add_database_items` | DB에 샘플 항목 추가 | database_id, items[] | page_ids[] |
| 6 | `apply_color_theme` | 색상 테마 적용 | page_id, theme | success |
| 7 | `link_databases` | DB 간 Relation 설정 | source_db, target_db, name | property_id |
| 8 | `generate_cover` | 커버 이미지 URL 생성 | theme, color, style | image_url |

### Tool 실행 순서 규칙

```
1. create_page (메인) → page_id 획득
2. create_page (하위) → sub_page_ids 획득 (병렬 가능)
3. create_database → database_ids 획득 (page_id 필요)
4. create_columns → 칼럼에 DB 배치 (page_id + database_id 필요)
5. add_blocks → 추가 블록 배치 (page_id 필요)
6. add_database_items → 샘플 데이터 (database_id 필요)
7. apply_color_theme → 마지막에 전체 적용
```

**의존성 그래프:**
```
create_page(main)
  ├─→ create_page(sub1) ─┐
  ├─→ create_page(sub2) ─┤ (병렬)
  ├─→ create_page(sub3) ─┘
  └─→ create_database ──→ create_columns ──→ add_blocks
                          └─→ add_database_items
                                              └─→ apply_color_theme
```

---

## 5. 색상 테마 매핑

### Notion API 지원 색상

```python
COLOR_THEMES = {
    "blue": {
        "background": "blue_background",
        "text": "blue",
        "cover_keywords": "sky, ocean, blue gradient",
        "korean": ["하늘색", "파란색", "블루"],
    },
    "orange": {
        "background": "orange_background",
        "text": "orange",
        "cover_keywords": "sunset, warm, orange gradient",
        "korean": ["주황색", "오렌지"],
    },
    "green": {
        "background": "green_background",
        "text": "green",
        "cover_keywords": "nature, forest, green gradient",
        "korean": ["초록색", "연두색", "그린"],
    },
    "red": {
        "background": "red_background",
        "text": "red",
        "cover_keywords": "warm red, coral",
        "korean": ["빨간색", "레드", "코랄"],
    },
    "purple": {
        "background": "purple_background",
        "text": "purple",
        "cover_keywords": "lavender, purple gradient",
        "korean": ["보라색", "퍼플", "라벤더"],
    },
    "pink": {
        "background": "pink_background",
        "text": "pink",
        "cover_keywords": "pink, cherry blossom",
        "korean": ["핑크", "분홍색"],
    },
    "yellow": {
        "background": "yellow_background",
        "text": "yellow",
        "cover_keywords": "sunshine, yellow gradient",
        "korean": ["노란색", "옐로우"],
    },
    "gray": {
        "background": "gray_background",
        "text": "gray",
        "cover_keywords": "minimal, monochrome",
        "korean": ["회색", "그레이", "모노"],
    },
}
```

---

## 6. 프롬프트 엔지니어링

### System Prompt (Agent 기본 성격)

```
당신은 NotionForge AI Agent입니다. 사용자의 요청을 받아 Notion 템플릿을 자동 생성합니다.

역할:
1. 사용자의 자연어 요청을 분석하여 의도를 파악합니다
2. 부족한 정보가 있으면 친절하게 질문합니다
3. 확인된 정보로 Template Blueprint를 생성합니다
4. Tool을 순서대로 호출하여 실제 Notion 페이지를 생성합니다

대화 스타일:
- 한국어로 대화합니다
- 친절하지만 간결하게 답합니다
- 구조를 제안할 때는 트리 형태로 보여줍니다
- 생성 전에 반드시 사용자 확인을 받습니다
- 불가능한 기능은 솔직히 말하고 대안을 제시합니다

제약사항:
- Notion API로 생성할 수 없는 요소: button 블록, synced 블록, 복잡한 formula
- DB 뷰는 기본 뷰만 생성 가능, 추가 뷰 설정은 사용자에게 안내
- Rate limit: 3 req/s, 블록 100개씩 배치 처리
```

### 확인 질문 전략

```
필수 질문 (confidence < 0.7):
- "어떤 용도의 템플릿인가요?"

선택 질문 (정보 보충):
- "색상 톤 선호가 있나요?" (미지정 시 기본 gray)
- "카테고리/태그 옵션을 알려주세요" (DB 포함 시)
- "하위 페이지도 필요한가요?" (복잡한 구조 시)
- "샘플 데이터를 몇 개 넣을까요?" (기본 5개)

질문은 최대 3개까지만. 너무 많이 물으면 UX 저하.
```
