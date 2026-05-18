# 테스트 가이드 (Test Guide)

> 최종 업데이트: 2026-05-18
> 테스트 현황: 1,374개 테스트, 80%+ 커버리지

---

## 테스트 구조

```
backend/tests/
├── unit/                          # 단위 테스트 (48 파일)
│   ├── test_ai_router.py         # AI 라우터 (프로바이더 감지, 모델 변경)
│   ├── test_agent_tools.py       # Tool Registry 11개 도구
│   ├── test_block_builder.py     # 블록 JSON 생성 (20종)
│   ├── test_blueprint_generator.py # Gen-Eval 피드백 루프
│   ├── test_chat_router.py       # WebSocket 채팅 (인증, 레이트리밋)
│   ├── test_copilot_client.py    # Copilot SDK 클라이언트
│   ├── test_database_ops.py      # DB CRUD (폴백 로직 포함)
│   ├── test_middleware.py        # Rate Limit, Request ID, 에러 정제
│   ├── test_notion_client.py     # Notion 클라이언트 (Mock + Real)
│   ├── test_notion_ops.py        # 페이지/블록/뷰 작업
│   ├── test_oauth_router.py      # OAuth CSRF, 토큰 교환
│   ├── test_providers.py         # LLM 프로바이더 4종 (OpenAI/Claude/Groq/Gemini)
│   ├── test_quality_validator.py # 3계층 검증 (Schema/Content/Design)
│   ├── test_tasks_router.py      # 비동기 작업 관리
│   ├── test_template_router.py   # 템플릿 생성 라우터
│   ├── test_workspace_router.py  # 워크스페이스 API
│   └── ...
├── integration/                   # 통합 테스트 (3 파일)
│   ├── test_api_endpoints.py     # REST API 엔드포인트
│   └── ...
└── conftest.py                    # 공통 픽스처
```

## 실행 방법

```bash
cd backend

# 전체 테스트
uv run pytest tests/ -v

# 단위 테스트만
uv run pytest tests/unit/ -v

# 커버리지 측정 (80% 미만 시 실패)
uv run pytest tests/ --cov=app --cov-fail-under=80

# HTML 커버리지 리포트
uv run pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html

# 특정 모듈 테스트
uv run pytest tests/unit/test_providers.py -v

# 키워드로 필터링
uv run pytest tests/ -k "oauth" -v
```

## 커버리지 현황 (v0.1.6)

| 모듈 | 커버리지 | 비고 |
|------|---------|------|
| `routers/ai.py` | 97% | 프로바이더 감지, 모델 변경 |
| `routers/oauth.py` | 98% | CSRF state 검증 |
| `routers/workspace.py` | 100% | 검색, 코멘트, 잠금, 아카이브 |
| `routers/chat.py` | 89% | WebSocket 인증/레이트리밋 |
| `routers/tasks.py` | 100% | 비동기 작업 관리 |
| `routers/template.py` | 82% | 파일 업로드 검증 |
| `core/middleware.py` | 100% | Rate Limit, Request ID |
| `notion/client.py` | 100% | Mock + Real 경로 |
| `notion/database_ops.py` | 96% | 폴백 로직 (속성 에러 복구) |
| `notion/view_ops.py` | 100% | 뷰 6종 CRUD |
| `agent/quality_validator.py` | 100% | 3계층 검증 |
| **전체** | **82%** | **fail_under=80%** |

## 테스트 작성 가이드

### 픽스처 패턴

```python
# Mock NotionClient 패턴
@pytest.fixture
def real_client():
    with patch("app.notion.client.settings") as mock_settings:
        mock_settings.notion_api_key = "ntn_test_token"
        mock_settings.notion_parent_page_id = "parent-id"
        with patch("notion_client.AsyncClient"):
            with patch("httpx.AsyncClient"):
                client = NotionClient(token="ntn_test_token", parent_page_id="parent-id")
    client._http_client = AsyncMock()
    client._http_legacy = AsyncMock()
    client.rate_limiter = AsyncMock()
    client.rate_limiter.acquire = AsyncMock()
    client.mock_mode = False
    return client

# ASGI 클라이언트 패턴 (라우터 테스트)
@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
```

### Body(embed=True) 엔드포인트 테스트

FastAPI의 `Body(embed=True)` 파라미터는 반드시 `json={"field_name": value}` 형태로 전송해야 합니다.

```python
# 올바른 방법
resp = await client.post("/api/endpoint", json={"api_key": "sk-test"})

# 잘못된 방법 (422 에러 발생)
resp = await client.post("/api/endpoint", json="sk-test")
```

### Rate Limiter 테스트 격리

미들웨어 상태가 테스트 간 공유되므로 초기화가 필요합니다.

```python
def _reset_rate_limiter():
    current = app.middleware_stack
    while current:
        if isinstance(current, RateLimitMiddleware):
            current._requests.clear()
            break
        current = getattr(current, "app", None)
```

## CI 파이프라인

```yaml
# .github/workflows/ci.yml (테스트 관련 부분)
- name: Run tests with coverage
  run: |
    cd backend
    uv run pytest tests/ --cov=app --cov-fail-under=80 --cov-report=xml
- name: Upload coverage
  uses: actions/upload-artifact@v4
  with:
    name: coverage-report
    path: backend/coverage.xml
```

## QA 체크리스트

### 생성 품질

| 검증 항목 | 검증 방법 |
|----------|----------|
| 페이지 제목/아이콘/커버 | 생성된 Notion 페이지 확인 |
| DB 속성 타입 정확성 | Notion에서 속성 타입 확인 |
| 샘플 데이터 3개+ | DB 항목 수 확인 |
| 뷰 설정 반영 | board/calendar/gallery 설정 확인 |
| 색상 테마 일관성 | 블록 배경색 확인 |
| Relation 연결 | DB 간 관계 속성 확인 |
| 서브페이지 내용 | 빈 페이지 없는지 확인 |

### 에러 복구

| 시나리오 | 기대 동작 |
|----------|----------|
| 잘못된 API 키 | 토큰 오류 안내 메시지 |
| Rate limit 초과 | 자동 재시도 후 성공 |
| AI 응답 파싱 실패 | Gen-Eval 재시도 (최대 3회) |
| Notion API 에러 | 속성 폴백 후 재시도 |
| WebSocket 끊김 | 자동 재연결 |
