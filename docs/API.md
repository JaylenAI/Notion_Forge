# API 명세 (API Specification)

> NotionForge 백엔드 REST / WebSocket API 엔드포인트

---

## Base URL

```
개발: http://localhost:8000
프로덕션: https://notionforge-api.railway.app (예정)
```

---

## 1. 채팅 API (WebSocket)

### `WS /ws/chat`

실시간 채팅 연결. AI와의 대화 및 생성 진행률 수신.

**연결:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat')
```

**클라이언트 → 서버 (메시지 전송)**
```json
{
  "type": "message",
  "content": "프로젝트 관리 대시보드 만들어줘, 주황색으로",
  "notion_token": "ntn_xxxx",
  "parent_page_id": "abc123"
}
```

**서버 → 클라이언트 (AI 응답)**
```json
{
  "type": "ai_response",
  "content": "프로젝트 관리 대시보드를 만들어드리겠습니다...",
  "metadata": {
    "intent": "CREATE",
    "template_type": "dashboard",
    "confidence": 0.95
  }
}
```

**서버 → 클라이언트 (생성 진행률)**
```json
{
  "type": "progress",
  "step": "create_database",
  "current": 3,
  "total": 8,
  "message": "프로젝트 DB 생성 중..."
}
```

**서버 → 클라이언트 (생성 완료)**
```json
{
  "type": "complete",
  "notion_url": "https://notion.so/xxxxx",
  "summary": {
    "pages_created": 4,
    "databases_created": 2,
    "blocks_created": 35,
    "duration_seconds": 12.5
  }
}
```

**서버 → 클라이언트 (에러)**
```json
{
  "type": "error",
  "code": "NOTION_API_ERROR",
  "message": "Notion API 연결에 실패했습니다. 토큰을 확인해주세요."
}
```

---

## 2. REST API

### 헬스체크

#### `GET /health`

```json
{
  "status": "ok",
  "version": "0.1.0",
  "notion_connected": true,
  "claude_connected": true
}
```

---

### 템플릿 생성 (동기)

#### `POST /api/templates/generate`

WebSocket 대신 REST로 생성할 때 사용.

**Request:**
```json
{
  "prompt": "습관 트래커 만들어줘, 파란색",
  "notion_token": "ntn_xxxx",
  "parent_page_id": "abc123",
  "options": {
    "include_sample_data": true,
    "sample_count": 5,
    "color_theme": "blue"
  }
}
```

**Response:**
```json
{
  "success": true,
  "notion_url": "https://notion.so/xxxxx",
  "page_id": "xxxxx",
  "summary": {
    "pages_created": 1,
    "databases_created": 1,
    "blocks_created": 15,
    "duration_seconds": 5.2
  },
  "blueprint": { "..." }
}
```

---

### Blueprint 미리보기

#### `POST /api/templates/preview`

생성 전에 Blueprint만 확인.

**Request:**
```json
{
  "prompt": "프로젝트 관리 대시보드, 주황색, 하위 페이지 3개"
}
```

**Response:**
```json
{
  "blueprint": {
    "title": "프로젝트 대시보드",
    "template_type": "dashboard",
    "color_theme": "orange",
    "structure": {
      "main_page": { "..." },
      "sub_pages": ["ETC", "Project", "Study"],
      "databases": [{ "..." }]
    },
    "estimated_api_calls": 25,
    "estimated_seconds": 12
  }
}
```

---

### 패턴 라이브러리 조회

#### `GET /api/patterns`

사용 가능한 템플릿 패턴 목록.

**Response:**
```json
{
  "patterns": [
    {
      "id": "dashboard",
      "name": "대시보드",
      "description": "갤러리 뷰 + 칼럼 레이아웃 + 네비게이션",
      "example_prompt": "프로젝트 관리 대시보드 만들어줘",
      "features": ["gallery_db", "column_layout", "sub_pages", "calendar"]
    },
    {
      "id": "tracker",
      "name": "트래커",
      "description": "습관/목표/학습 추적용",
      "example_prompt": "습관 트래커 만들어줘",
      "features": ["checkbox_db", "stats", "date_filter"]
    }
  ]
}
```

---

### 템플릿 수정

#### `POST /api/templates/{page_id}/modify`

기존 생성된 템플릿에 추가/수정.

**Request:**
```json
{
  "prompt": "DB에 '우선순위' select 속성 추가해줘. 높음/중간/낮음으로.",
  "notion_token": "ntn_xxxx",
  "page_id": "xxxxx"
}
```

**Response:**
```json
{
  "success": true,
  "modifications": [
    {
      "action": "add_property",
      "target": "database:xxxxx",
      "property": "우선순위",
      "type": "select",
      "options": ["높음", "중간", "낮음"]
    }
  ]
}
```

---

## 3. 에러 코드

| 코드 | HTTP | 설명 |
|------|------|------|
| `NOTION_AUTH_FAILED` | 401 | Notion 토큰 무효 |
| `NOTION_PAGE_NOT_FOUND` | 404 | 부모 페이지 없음 or 권한 없음 |
| `NOTION_RATE_LIMITED` | 429 | API rate limit (자동 재시도) |
| `CLAUDE_AUTH_FAILED` | 401 | Claude API 키 무효 |
| `CLAUDE_ERROR` | 500 | AI 응답 에러 |
| `BLUEPRINT_INVALID` | 422 | 생성된 Blueprint 검증 실패 |
| `GENERATION_FAILED` | 500 | 템플릿 생성 중 에러 |
| `VALIDATION_ERROR` | 422 | 입력값 검증 실패 |
