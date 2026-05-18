# API Reference

> NotionForge 백엔드 REST / WebSocket API

---

## Base URL

```
개발:      http://localhost:9500
프로덕션:  https://your-domain.com (리버스 프록시 뒤)
```

---

## Health Endpoints

### `GET /health`

전체 시스템 상태 + 통계.

```json
{
  "status": "ok",
  "version": "0.1.6",
  "ai_provider": "copilot",
  "notion_ready": true,
  "copilot": { "available": true, "started": true },
  "features": 78,
  "skills": 48,
  "today_stats": { "total": 15, "success": 12, "success_rate": 80.0 }
}
```

### `GET /health/ready`

Kubernetes readiness probe. AI provider + Notion 설정 확인.

```json
{ "ready": true, "checks": { "notion_configured": true, "ai_provider_configured": true } }
```

### `GET /health/live`

Kubernetes liveness probe.

```json
{ "alive": true }
```

---

## 1. WebSocket Chat API

### `WS /ws/chat`

실시간 AI 채팅 + 템플릿 생성 진행률.

**연결:**
```javascript
const ws = new WebSocket('ws://localhost:9500/ws/chat')
```

**클라이언트 → 서버: 초기화**
```json
{
  "type": "init",
  "notion_token": "ntn_xxxx",
  "parent_page_id": "abc123-...",
  "settings": { "complexity": "standard", "language": "ko" }
}
```

**클라이언트 → 서버: 메시지**
```json
{ "type": "message", "content": "프로젝트 관리 대시보드 만들어줘" }
```

**서버 → 클라이언트: AI 응답**
```json
{ "type": "ai_response", "content": "프로젝트 관리 대시보드를 만들어드리겠습니다..." }
```

**서버 → 클라이언트: 승인 요청**
```json
{
  "type": "approval_request",
  "content": "다음 템플릿을 생성할까요?",
  "metadata": { "template_type": "dashboard", "databases": 2, "pages": 4 }
}
```

**서버 → 클라이언트: 진행률**
```json
{ "type": "progress", "step": "create_database", "current": 3, "total": 8, "message": "프로젝트 DB 생성 중..." }
```

**서버 → 클라이언트: 완료**
```json
{
  "type": "complete",
  "notion_url": "https://notion.so/xxxxx",
  "summary": { "pages_created": 4, "databases_created": 2, "blocks_created": 35, "duration_seconds": 12.5 }
}
```

**서버 → 클라이언트: 에러**
```json
{ "type": "error", "content": "Notion API 연결에 실패했습니다." }
```

---

## 2. Template API

### `POST /api/templates/generate`

동기 템플릿 생성 (타임아웃 180초).

**Request:**
```json
{
  "prompt": "습관 트래커 만들어줘",
  "notion_token": "ntn_xxxx",
  "parent_page_id": "abc123-...",
  "options": { "include_sample_data": true, "sample_count": 5 }
}
```

**Response (200):**
```json
{
  "success": true,
  "notion_url": "https://notion.so/xxxxx",
  "page_id": "xxxxx",
  "summary": { "pages": 1, "databases": 1, "blocks": 15, "duration_seconds": 5.2 }
}
```

### `POST /api/templates/generate/stream`

SSE(Server-Sent Events) 스트리밍 생성.

**Request:** 동일

**Response:** `text/event-stream`
```
data: {"type":"progress","step":"analyzing","message":"의도 분석 중..."}
data: {"type":"progress","step":"generating","message":"블루프린트 생성 중..."}
data: {"type":"complete","notion_url":"https://notion.so/xxx","summary":{...}}
```

### `POST /api/templates/preview`

생성 전 블루프린트 미리보기.

**Request:**
```json
{ "prompt": "프로젝트 관리 대시보드" }
```

**Response:**
```json
{
  "blueprint": {
    "title": "프로젝트 대시보드",
    "template_type": "dashboard",
    "databases": [...],
    "sub_pages": [...]
  }
}
```

### `POST /api/templates/{page_id}/modify`

기존 템플릿 수정.

**Request:**
```json
{
  "prompt": "DB에 '우선순위' select 속성 추가해줘",
  "notion_token": "ntn_xxxx",
  "page_id": "xxxxx"
}
```

### `POST /api/templates/document-to-notion`

파일 업로드 → Notion 변환.

**Request:** `multipart/form-data`
- `file`: 업로드 파일 (.txt, .md, .csv)
- `notion_token`: Notion 토큰
- `parent_page_id`: 대상 페이지 ID

---

## 3. Tasks API (비동기 작업)

120초 초과 가능한 복잡한 생성 작업용 비동기 패턴.

### `POST /api/tasks/submit`

작업 제출.

**Request:**
```json
{
  "prompt": "5개 DB + 하위 페이지 10개 대시보드",
  "notion_token": "ntn_xxxx",
  "parent_page_id": "abc123-..."
}
```

**Response:**
```json
{
  "task_id": "a1b2c3d4e5f6",
  "status": "pending",
  "progress": [],
  "created_at": 1714900000.0
}
```

### `GET /api/tasks/{task_id}`

작업 상태 폴링.

**Response:**
```json
{
  "task_id": "a1b2c3d4e5f6",
  "status": "completed",
  "progress": [
    { "step": "blueprint", "message": "블루프린트 생성 완료", "timestamp": 1714900010.0 }
  ],
  "result": { "success": true, "notion_url": "https://notion.so/xxx" },
  "completed_at": 1714900025.0
}
```

**상태값:** `pending` → `running` → `completed` | `failed` | `cancelled`

### `DELETE /api/tasks/{task_id}`

작업 취소/삭제.

---

## 4. AI Provider API

### `POST /api/templates/ai/detect-provider`

API 키로 프로바이더 감지 + 모델 목록 조회.

**Request:**
```json
{ "api_key": "sk-xxx..." }
```

**Response:**
```json
{ "provider": "openai", "models": [{ "id": "gpt-4.1", "name": "gpt-4.1" }] }
```

### `GET /api/templates/ai/copilot-status`

Copilot SDK 상태 조회.

```json
{ "available": true, "started": true, "models": ["gpt-4.1", "gpt-5-mini", "claude-sonnet-4-5"] }
```

### `POST /api/templates/ai/copilot-model`

Copilot 모델 변경 (세션 단위).

**Request:**
```json
{ "model": "gpt-4.1" }
```

---

## 5. Recipes API

### `GET /api/recipes`

레시피 목록 조회.

**Query params:** `category`, `search`

**Response:**
```json
[
  {
    "id": "project-dashboard",
    "name": "프로젝트 대시보드",
    "description": "팀 프로젝트 관리용 대시보드",
    "category": "productivity",
    "icon": "📊",
    "tags": ["project", "team"],
    "complexity": "advanced"
  }
]
```

### `GET /api/recipes/{recipe_id}`

단일 레시피 상세 (블루프린트 포함).

### `POST /api/recipes/{recipe_id}/generate`

레시피로 즉시 생성.

**Request:**
```json
{ "notion_token": "ntn_xxxx", "parent_page_id": "abc123-..." }
```

---

## 6. Skills API

### `GET /api/skills`

스킬 목록 조회.

```json
{
  "skills": {
    "project_management": { "description": "프로젝트 관리", "keywords": ["project", "task"] },
    "habit_tracker": { "description": "습관 추적기", "keywords": ["habit", "routine"] }
  }
}
```

### `GET /api/skills/{skill_id}`

스킬 상세 (내용 + 커스텀 여부).

### `POST /api/skills`

커스텀 스킬 생성.

**Request:**
```json
{
  "skill_id": "meeting_notes",
  "name": "회의록",
  "description": "회의록 생성 스킬",
  "keywords": "회의,미팅,meeting",
  "content": "# 회의록 템플릿..."
}
```

### `PUT /api/skills/{skill_id}`

커스텀 스킬 수정. (Request 동일)

### `DELETE /api/skills/{skill_id}`

커스텀 스킬 삭제.

---

## 7. OAuth API

### `GET /api/oauth/authorize`

Notion OAuth 인증 시작. 브라우저를 Notion 인증 페이지로 리디렉트.

### `GET /api/oauth/callback?code=xxx&state=xxx`

OAuth 콜백. CSRF state 검증 후 일회용 교환 코드 발급, 프론트엔드로 리디렉트 (`?oauth_callback=true&code=xxx`).

### `POST /api/oauth/exchange?code=xxx`

일회용 코드를 OAuth 토큰으로 교환. 토큰이 URL에 노출되지 않도록 보호.

```json
{
  "oauth_token": "ntn_xxxxx",
  "workspace_name": "My Workspace",
  "workspace_id": "xxxxx"
}
```

| 상태 | 의미 |
|------|------|
| 200 | 성공 |
| 400 | 유효하지 않은 코드 |
| 410 | 만료된 코드 (60초 TTL) |

### `GET /api/oauth/status`

OAuth 설정 상태.

```json
{ "oauth_configured": true, "redirect_uri": "http://localhost:9500/api/oauth/callback" }
```

---

## 8. Workspace API

### `GET /api/templates/search?q=keyword`

워크스페이스 검색.

### `POST /api/templates/{page_id}/comment`

페이지에 코멘트 추가.

### `POST /api/templates/{page_id}/lock`

페이지 잠금/해제. Query: `locked=true|false`

### `POST /api/templates/{page_id}/archive`

페이지 아카이브.

---

## 9. Metrics API

### `GET /api/metrics/summary`

최근 7일 생성 통계.

```json
{
  "period": "7d",
  "total_generations": 50,
  "success_count": 42,
  "success_rate": 84.0,
  "avg_duration_ms": 8500,
  "top_skills": { "project_management": 15, "habit_tracker": 8 }
}
```

---

## Error Codes

| HTTP | 코드 | 설명 |
|------|------|------|
| 400 | `INVALID_INPUT` | 잘못된 입력값 |
| 401 | `NOTION_AUTH_FAILED` | Notion 토큰 무효 |
| 404 | `NOT_FOUND` | 리소스 없음 |
| 413 | `FILE_TOO_LARGE` | 파일 크기 초과 (10MB) |
| 422 | `VALIDATION_ERROR` | Pydantic 검증 실패 |
| 429 | `RATE_LIMITED` | 요청 한도 초과 |
| 500 | `INTERNAL_ERROR` | 서버 내부 에러 |
| 504 | `TIMEOUT` | 생성 타임아웃 (180초) |

---

## Rate Limiting

- 기본: 60 requests/minute (IP 기준)
- 초과 시: `429 Too Many Requests` + `Retry-After` 헤더
- WebSocket: 연결당 20 messages/minute
- Health 엔드포인트: 제한 없음
- 설정: `RATE_LIMIT_RPM` 환경변수
