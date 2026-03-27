# 환경 세팅 + 배포 가이드 (Setup & Deploy)

> 로컬 개발 환경 세팅 (5분) + 프로덕션 배포 방법

---

# Part 1: 로컬 개발 환경

## 사전 요구사항

| 도구 | 최소 버전 | 확인 명령 | 비고 |
|------|----------|----------|------|
| Docker | 24+ | `docker --version` | 필수 |
| Docker Compose | v2+ | `docker compose version` | 필수 |
| uv | 최신 | `uv --version` | Python 패키지 관리 |
| Node.js | 18+ | `node --version` | 프론트엔드 |
| Git | 2.x | `git --version` | |

---

## 1. Notion Integration 생성 (최초 1회)

1. https://www.notion.so/my-integrations 접속
2. "New integration" → Name: `NotionForge`
3. Capabilities: **Read/Update/Insert content** 모두 체크
4. "Submit" → **Internal Integration Secret** 복사 (`ntn_xxxx`)
5. Notion에서 부모 페이지 열기 → `...` → "Add connections" → `NotionForge` 선택

> **부모 페이지 ID 확인**: URL `https://notion.so/My-Page-abc123def456`에서 마지막 부분

---

## 2. Claude API 키 발급

1. https://console.anthropic.com → API Keys → "Create Key"
2. 키 복사 (`sk-ant-xxxx`)

---

## 3. 프로젝트 클론 & 환경 설정

```bash
git clone https://github.com/{username}/notionforge.git
cd notionforge
cp .env.example .env
# .env에 NOTION_API_KEY, ANTHROPIC_API_KEY 등 입력
```

---

## 4. 방법 1: Docker로 실행 (권장)

### docker-compose.yml 구조

```yaml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./backend:/app
    command: uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev -- --host
    depends_on:
      - backend
```

### Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# uv 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 의존성 설치
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# 소스 복사
COPY . .

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

```dockerfile
FROM node:18-slim

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
```

### 실행

```bash
# 전체 실행 (원커맨드)
docker compose up -d

# 로그 확인
docker compose logs -f

# 중지
docker compose down
```

---

## 5. 방법 2: 로컬 직접 실행 (uv)

### Backend

```bash
cd backend
uv sync                  # 의존성 설치
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (별도 터미널)

```bash
cd frontend
npm install
npm run dev
```

---

## 6. 접속 확인

| 서비스 | URL |
|--------|-----|
| 프론트엔드 (채팅 UI) | http://localhost:5173 |
| 백엔드 API | http://localhost:8000 |
| API 문서 (Swagger) | http://localhost:8000/docs |

```bash
# 헬스체크
curl http://localhost:8000/health
```

---

## 7. Notion MCP 서버 설정 (선택)

`~/.claude.json` 또는 `.claude/settings.json`에 추가:

```json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": {
        "OPENAPI_MCP_HEADERS": "{\"Authorization\": \"Bearer ntn_xxxx\", \"Notion-Version\": \"2022-06-28\"}"
      }
    }
  }
}
```

---

## 8. 유용한 명령어

```bash
# Docker 환경
docker compose exec backend uv run pytest              # 테스트
docker compose exec backend uv run ruff check .        # 린트
docker compose exec frontend npm run build             # 빌드 확인

# 로컬 환경
cd backend && uv run pytest                            # 테스트
cd backend && uv run ruff check .                      # 린트
cd frontend && npm run build                           # 빌드 확인

# Notion API 연결 테스트
cd backend && uv run python -c "
from notion_client import Client
client = Client(auth='ntn_xxxx')
print(client.users.me())
"
```

---

## 9. 트러블슈팅

| 에러 | 원인 | 해결 |
|------|------|------|
| Notion 403 Forbidden | Integration 미연결 | 페이지 → ... → Add connections |
| Notion 429 Rate Limited | 초당 3회 초과 | 자동 백오프 (정상 동작) |
| CORS 에러 | 백엔드 CORS 설정 | main.py CORSMiddleware 확인 |
| Claude 401 | API 키 문제 | .env ANTHROPIC_API_KEY 확인 |
| Docker port 충돌 | 포트 이미 사용 중 | `lsof -i :8000` 확인 후 종료 |

---

# Part 2: 프로덕션 배포

## Backend → Railway (무료)

1. https://railway.app → GitHub 로그인
2. "New Project" → GitHub 레포 → Root: `backend`
3. Dockerfile 감지 → 자동 빌드
4. Variables: `ANTHROPIC_API_KEY`, `PORT=8000`

---

## Frontend → Vercel (무료)

1. https://vercel.com → GitHub 레포 → Root: `frontend`
2. Framework: Vite
3. Variables:
   ```
   VITE_API_URL=https://notionforge-api-xxx.up.railway.app
   VITE_WS_URL=wss://notionforge-api-xxx.up.railway.app
   ```

---

## CI/CD (GitHub Actions)

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  backend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: cd backend && uv sync
      - run: cd backend && uv run pytest tests/unit/ -v

  frontend-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '18' }
      - run: cd frontend && npm ci && npm run build && npm run lint
```

---

## 비용 요약

| 항목 | 비용 |
|------|------|
| Notion API | **무료** |
| Docker | **무료** |
| uv | **무료** |
| Railway (Backend) | **무료** ($5 크레딧/월) |
| Vercel (Frontend) | **무료** (Hobby) |
| GitHub Actions | **무료** (2,000분/월) |
| Claude API | **사용량 과금** |
| **합계 (API 제외)** | **$0/월** |
