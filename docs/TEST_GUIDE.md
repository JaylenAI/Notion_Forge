# 테스트 + QA 가이드 (Test & QA Guide)

> 단위/통합/E2E 테스트 실행 방법 + 템플릿 품질 검증 체크리스트

---

# Part 1: 테스트

## 테스트 구조

```
backend/tests/
├── unit/
│   ├── test_intent_analyzer.py
│   ├── test_blueprint_generator.py
│   ├── test_block_builder.py
│   ├── test_color_theme.py
│   └── test_rate_limiter.py
├── integration/
│   ├── test_notion_client.py
│   ├── test_claude_agent.py
│   └── test_template_generation.py
├── e2e/
│   └── test_chat_flow.py
├── fixtures/
│   ├── sample_blueprints.json
│   └── mock_notion_responses.json
└── conftest.py
```

## 실행 방법

```bash
cd backend

# 전체 테스트
uv run pytest

# 단위 테스트만
uv run pytest tests/unit/ -v

# 통합 테스트 (Notion API 실제 호출, .env 필요)
uv run pytest tests/integration/ -v --timeout=30

# E2E (Backend + Frontend 실행 상태에서)
uv run pytest tests/e2e/ -v --timeout=60

# 커버리지 (목표: 80%+)
uv run pytest --cov=. --cov-report=html
open htmlcov/index.html
```

## 핵심 테스트 케이스

### Intent Analyzer

```python
def test_create_intent():
    result = analyze("프로젝트 관리 대시보드 만들어줘")
    assert result["intent"] == "CREATE"
    assert result["template_type"] == "dashboard"
    assert result["confidence"] >= 0.8

def test_color_theme_korean():
    result = analyze("하늘색으로 만들어줘")
    assert result["color_theme"] == "blue"

def test_ambiguous_request():
    result = analyze("노션 만들어줘")
    assert result["confidence"] < 0.7
    assert len(result["missing_info"]) > 0
```

### Block Builder

```python
def test_heading_block():
    block = build_heading("Project", level=1, color="orange_background")
    assert block["type"] == "heading_1"
    assert block["heading_1"]["color"] == "orange_background"

def test_column_layout():
    blocks = build_columns(2, [["블록A"], ["블록B"]])
    assert blocks[0]["type"] == "column_list"
    assert len(blocks[0]["column_list"]["children"]) == 2

def test_database_properties():
    props = build_properties({"이름": "title", "카테고리": {"type": "select", "options": ["A", "B"]}})
    assert props["이름"]["type"] == "title"
    assert len(props["카테고리"]["select"]["options"]) == 2
```

### Notion 통합 테스트

```python
def test_create_page(cleanup_pages):
    page = create_page(title="테스트", icon="🧪", cover_url="https://...")
    cleanup_pages.append(page["id"])  # 테스트 후 자동 archive
    assert page["id"] is not None

def test_rate_limit_handling():
    # 빠르게 여러 요청 → 429 → 재시도 → 성공 확인
```

## 테스트 환경 분리

```
NOTION_TEST_PAGE_ID=xxxx    # 테스트 전용 부모 페이지
```

테스트 후 생성된 페이지는 자동 archive 처리.

---

# Part 2: QA 체크리스트

## 기본 생성 품질

### 페이지

| # | 항목 | 상태 |
|---|------|------|
| 1 | 페이지 제목 정확 | ❌ |
| 2 | 아이콘 설정됨 | ❌ |
| 3 | 커버 이미지 표시 | ❌ |
| 4 | 부모 페이지 아래 생성 | ❌ |

### 데이터베이스

| # | 항목 | 상태 |
|---|------|------|
| 5 | DB 제목 정확 | ❌ |
| 6 | 요청한 속성 모두 존재 | ❌ |
| 7 | 속성 타입 정확 | ❌ |
| 8 | Select 옵션 + 색상 | ❌ |
| 9 | 샘플 데이터 입력됨 | ❌ |

### 레이아웃 & 디자인

| # | 항목 | 상태 |
|---|------|------|
| 10 | 칼럼 레이아웃 정상 | ❌ |
| 11 | 블록 순서 올바름 | ❌ |
| 12 | 색상 테마 일관적 | ❌ |
| 13 | 하위 페이지 링크 정상 | ❌ |
| 14 | Relation 정상 연결 | ❌ |

## 시나리오별 QA

### A. 대시보드

입력: `"프로젝트 대시보드, 주황색, 하위 페이지 3개"`

| 검증 | 기대값 | 상태 |
|------|--------|------|
| 메인 페이지 | 제목 + 아이콘 + 커버 | ❌ |
| 칼럼 | 2단 (좌30/우70) | ❌ |
| 갤러리 DB | 속성 + 샘플 | ❌ |
| 색상 | orange_background | ❌ |
| 하위 3개 | 각각 독립 구조 | ❌ |

### B. 북마크 사이트

입력: `"북마크 정리, 카테고리별, 즐겨찾기"`

| 검증 | 기대값 | 상태 |
|------|--------|------|
| 카테고리 목록 | 좌측 배치 | ❌ |
| 갤러리 DB | 커버 카드 | ❌ |
| 즐겨찾기 | checkbox 속성 | ❌ |
| URL | url 속성 | ❌ |

### C. Tea Note 스타일

입력: `"차 시음 기록, 초록색, 종류별"`

| 검증 | 기대값 | 상태 |
|------|--------|------|
| 커버 | 초록색 톤 | ❌ |
| Quick Action | 좌측 배치 | ❌ |
| 종류 select | 요청 옵션 포함 | ❌ |
| 하위 페이지 | 인벤토리, 일기장 | ❌ |

## 에러 케이스 QA

| 입력 | 기대 동작 | 상태 |
|------|----------|------|
| 빈 메시지 | 안내 응답 | ❌ |
| 잘못된 토큰 | 토큰 오류 안내 | ❌ |
| "버튼 넣어줘" | API 제한 안내 + 대안 | ❌ |
| 극히 복잡한 요청 | 단계별 분할 제안 | ❌ |
| Rate limit 초과 | 자동 재시도 + 대기 안내 | ❌ |
