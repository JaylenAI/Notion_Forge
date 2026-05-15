# Deployment Guide

NotionForge 프로덕션 배포 가이드.

---

## 배포 방법 선택

| 방법 | 난이도 | 추천 환경 |
|------|--------|----------|
| Docker Compose | 쉬움 | VPS, 홈서버 |
| 직접 실행 (uv + nginx) | 보통 | 커스터마이징 필요 시 |
| Kubernetes | 고급 | 대규모, HA 필요 시 |

---

## 1. Docker Compose (권장)

### 사전 요구사항

- Docker 24+
- Docker Compose v2+
- 최소 1GB RAM, 1 vCPU

### 배포 절차

```bash
# 1. 클론
git clone https://github.com/hanseungheon/NotionForge.git
cd NotionForge

# 2. 환경변수 설정
cp .env.example .env
# .env 파일을 열어 필수값 입력 (NOTION_API_KEY, NOTION_PARENT_PAGE_ID)

# 3. 프로덕션 실행
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 4. 상태 확인
curl http://localhost:9500/health
curl http://localhost:9500/health/ready
```

### 프로덕션 설정 차이점

| 항목 | 개발 | 프로덕션 |
|------|------|----------|
| 로그 레벨 | INFO | WARNING |
| 백엔드 메모리 | 512M | 1G |
| 프론트엔드 포트 | 9501 | 80 (nginx) |
| 재시작 정책 | unless-stopped | always |
| Health check | /health | /health/live |

### 업데이트

```bash
git pull origin dev
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

---

## 2. 직접 실행 (uv + nginx)

### Backend

```bash
cd backend
uv sync --no-dev  # 프로덕션 의존성만 설치

# systemd 서비스 또는 직접 실행
uv run uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 9500 \
  --workers 2 \
  --log-level warning
```

### Frontend

```bash
cd frontend
npm ci
npm run build

# 빌드 결과물을 nginx로 서빙
# dist/ 폴더를 웹서버 루트로 설정
```

### systemd 서비스 예시

```ini
# /etc/systemd/system/notionforge.service
[Unit]
Description=NotionForge Backend
After=network.target

[Service]
Type=exec
WorkingDirectory=/opt/notionforge/backend
EnvironmentFile=/opt/notionforge/.env
ExecStart=/opt/notionforge/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 9500 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

## 3. Reverse Proxy (nginx)

프로덕션에서는 반드시 리버스 프록시를 사용하세요.

```nginx
# /etc/nginx/sites-available/notionforge
server {
    listen 443 ssl http2;
    server_name notionforge.example.com;

    ssl_certificate /etc/letsencrypt/live/notionforge.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/notionforge.example.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://127.0.0.1:9501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:9500;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE 지원
        proxy_read_timeout 300s;
        proxy_buffering off;
    }

    # WebSocket
    location /ws {
        proxy_pass http://127.0.0.1:9500;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 3600s;
    }

    # Health (내부망만 허용 권장)
    location /health {
        proxy_pass http://127.0.0.1:9500;
        allow 127.0.0.1;
        allow 10.0.0.0/8;
        deny all;
    }
}
```

---

## 4. Kubernetes

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notionforge-backend
spec:
  replicas: 1  # 단일 인스턴스 권장 (in-memory store)
  selector:
    matchLabels:
      app: notionforge-backend
  template:
    metadata:
      labels:
        app: notionforge-backend
    spec:
      containers:
        - name: backend
          image: ghcr.io/jaylenai/notionforge-backend:latest
          ports:
            - containerPort: 9500
          envFrom:
            - secretRef:
                name: notionforge-secrets
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "2000m"
          livenessProbe:
            httpGet:
              path: /health/live
              port: 9500
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 9500
            initialDelaySeconds: 5
            periodSeconds: 10
```

### Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: notionforge-secrets
type: Opaque
stringData:
  NOTION_API_KEY: "ntn_xxxx"
  NOTION_PARENT_PAGE_ID: "your-page-id"
  GROQ_API_KEY: "gsk_xxxx"
```

---

## 환경변수 전체 목록

| 변수 | 필수 | 기본값 | 설명 |
|------|------|--------|------|
| `NOTION_API_KEY` | O | - | Notion Integration 토큰 |
| `NOTION_PARENT_PAGE_ID` | O | - | 템플릿 생성 대상 페이지 ID |
| `COPILOT_ENABLED` | - | true | GitHub Copilot SDK 사용 여부 |
| `COPILOT_MODEL` | - | gpt-4.1 | Copilot 기본 모델 |
| `ANTHROPIC_API_KEY` | - | - | Claude API 키 |
| `GEMINI_API_KEY` | - | - | Google Gemini API 키 |
| `GROQ_API_KEY` | - | - | Groq API 키 |
| `BACKEND_PORT` | - | 9500 | 백엔드 포트 |
| `FRONTEND_PORT` | - | 9501 | 프론트엔드 포트 |
| `FRONTEND_URL` | - | http://localhost:9501 | CORS/OAuth 리디렉트 URL |
| `LOG_LEVEL` | - | INFO | 로그 레벨 (DEBUG/INFO/WARNING/ERROR) |
| `UNSPLASH_ACCESS_KEY` | - | - | 커버 이미지 자동 검색용 |
| `NOTION_OAUTH_CLIENT_ID` | - | - | OAuth 연동 시 클라이언트 ID |
| `NOTION_OAUTH_CLIENT_SECRET` | - | - | OAuth 연동 시 시크릿 |
| `RATE_LIMIT_RPM` | - | 60 | 분당 최대 요청 수 |

---

## Health Check 엔드포인트

| 엔드포인트 | 용도 | 응답 예시 |
|-----------|------|----------|
| `GET /health` | 전체 상태 + 통계 | `{"status":"ok","version":"8.0.0",...}` |
| `GET /health/ready` | K8s readiness probe | `{"ready":true,"checks":{...}}` |
| `GET /health/live` | K8s liveness probe | `{"alive":true}` |

---

## 리소스 요구사항

| 구성 | CPU | RAM | 디스크 |
|------|-----|-----|--------|
| 최소 | 1 vCPU | 1 GB | 1 GB |
| 권장 | 2 vCPU | 2 GB | 5 GB |
| 높은 부하 | 4 vCPU | 4 GB | 10 GB |

---

## 데이터 백업

NotionForge는 다음 파일에 상태를 저장합니다:

```
backend/data/
  episodes.jsonl      # 생성 이력
  preferences.json    # 사용자 설정
  skill_stats.json    # 스킬 사용 통계
  custom_skills/      # 커스텀 스킬 디렉토리
```

Docker 사용 시 `backend_data` 볼륨을 백업하세요:

```bash
docker run --rm -v notionforge_backend_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/notionforge-backup-$(date +%Y%m%d).tar.gz /data
```

---

## 문제 해결

### 자주 발생하는 문제

**1. Notion API 연결 실패**
```
에러: "Notion API 연결에 실패했습니다"
해결: NOTION_API_KEY 확인 + 대상 페이지에 Integration 연결 확인
```

**2. AI Provider 없음**
```
에러: "사용 가능한 AI 프로바이더가 없습니다"
해결: COPILOT_ENABLED=true 확인 또는 다른 API 키 설정
```

**3. WebSocket 연결 끊김**
```
에러: 프론트엔드에서 연결 실패
해결: nginx에서 WebSocket 업그레이드 헤더 설정 확인
     proxy_set_header Upgrade $http_upgrade;
     proxy_set_header Connection "upgrade";
```

**4. CORS 에러**
```
에러: "Access-Control-Allow-Origin" 관련
해결: .env에서 FRONTEND_URL을 실제 프론트엔드 도메인으로 설정
```

**5. 메모리 부족**
```
에러: OOMKilled (Docker/K8s)
해결: 메모리 제한 상향 (최소 512MB, 권장 1GB)
```
