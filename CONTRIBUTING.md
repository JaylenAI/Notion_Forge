# Contributing to NotionForge

NotionForge에 기여해주셔서 감사합니다!

## 개발 환경 설정

### 사전 요구사항
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (패키지 관리)
- Node.js 18+ (프론트엔드)

### 설치

```bash
git clone https://github.com/JaylenAI/notion_ai_agent.git
cd notion_ai_agent

# Backend
cd backend
uv sync
cp ../.env.example ../.env  # 환경변수 설정

# Frontend
cd ../frontend
npm install
```

### 실행

```bash
# Backend
cd backend
uv run uvicorn app.main:app --port 9500 --reload

# Frontend (별도 터미널)
cd frontend
npm run dev
```

## 개발 워크플로우

### 브랜치 전략

```
main     <- 안정 릴리스 (태그로 버전 관리)
  └── dev  <- 통합 브랜치
       ├── feature/기능명
       ├── fix/버그명
       └── refactor/대상
```

1. `dev`에서 feature 브랜치 생성
2. 개발 + 테스트
3. PR → `dev`로 머지
4. 릴리스 시 `dev` → `main` 머지 + 태그

### 커밋 컨벤션

```
<type>: <설명>

Types: feat, fix, refactor, docs, test, chore, perf, ci
```

### 코드 품질

PR 제출 전 반드시 확인:

```bash
cd backend

# 테스트
uv run pytest tests/ -v

# Lint
uv run ruff check .

# Format
uv run ruff format .
```

## 기여 가이드라인

### 새 기능 추가
1. Issue에서 논의 먼저
2. 테스트 먼저 작성 (TDD)
3. 구현
4. 문서 업데이트
5. PR 제출

### 버그 수정
1. 재현 가능한 테스트 케이스 작성
2. 수정
3. 테스트 통과 확인
4. PR 제출

### 새 AI 프로바이더 추가
1. `app/agent/providers/` 에 새 프로바이더 파일 생성
2. `BaseProvider` 상속 + `call()` 구현
3. `router.py`의 `create_provider()`에 등록
4. 테스트 추가

### 새 스킬 추가
1. `app/skills/` 에 스킬 디렉토리 생성
2. `SKILL.md` 패턴 파일 작성
3. `__init__.py`에 등록
4. 테스트로 스킬 매칭 확인

## 코드 스타일

- Python: ruff (black 호환 포맷)
- 함수 50줄 이하
- 파일 800줄 이하
- 에러 핸들링 필수
- 하드코딩 금지 (환경변수 사용)

## 질문이 있으시면

- [Issues](https://github.com/JaylenAI/notion_ai_agent/issues)에서 질문해주세요
- 버그 리포트는 Issue 템플릿을 사용해주세요
