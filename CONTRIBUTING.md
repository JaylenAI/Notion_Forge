# Contributing to NotionForge

NotionForge에 기여해주셔서 감사합니다!

## 개발 환경 설정

### 사전 요구사항
- Python 3.11+
- Node.js 20+
- [uv](https://docs.astral.sh/uv/) (Python 패키지 매니저)

### 로컬 설정

```bash
# 저장소 클론
git clone https://github.com/JaylenAI/notion_ai_agent.git
cd notion_ai_agent

# 환경변수 설정
cp .env.example .env
# .env 파일에 Notion API 키와 AI Provider 키를 입력

# Backend 실행
cd backend
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 9500 --reload

# Frontend 실행 (별도 터미널)
cd frontend
npm install
npm run dev
```

### Docker로 실행

```bash
cp .env.example .env
# .env 파일 편집
docker compose up --build
```

## 프로젝트 구조

```
backend/
  app/
    agent/          # AI 에이전트 (orchestrator, blueprint, pipeline)
    core/           # 설정, 로깅, 메트릭
    notion/         # Notion API 클라이언트
    routers/        # FastAPI 라우터
    skills/         # 48개 스킬 (SKILL.md)
    schemas/        # Pydantic 모델
frontend/
  src/
    components/     # React 컴포넌트
    stores/         # Zustand 스토어
```

## 기여 방법

### 1. Issue 생성
- 버그 리포트 또는 기능 제안은 GitHub Issue로 생성해주세요
- 템플릿을 사용하여 필요한 정보를 작성해주세요

### 2. Pull Request
1. Fork 후 feature 브랜치 생성 (`git checkout -b feat/my-feature`)
2. 변경사항 커밋 (한글 커밋 메시지 사용)
3. 테스트 실행 (`uv run pytest tests/ -q`)
4. PR 생성

### 3. 커스텀 스킬 추가
1. `backend/app/skills/{스킬명}/SKILL.md` 생성
2. YAML frontmatter + DB Properties + Views + Block Order 작성
3. `backend/app/skills/__init__.py`의 SKILL_REGISTRY에 등록
4. `TIER2_SKILLS` set에 추가 (세분화 스킬인 경우)

## 코드 스타일

- Backend: [Ruff](https://docs.astral.sh/ruff/) (`uv run ruff check .`)
- Frontend: ESLint + Prettier
- 커밋 메시지: `<type>: <한글 설명>` (feat, fix, refactor, docs, test, chore)

## 테스트

```bash
# 유닛 테스트
cd backend
uv run pytest tests/ -q

# 커버리지
uv run pytest tests/ --cov=app --cov-report=term-missing
```

## 라이선스

MIT License
