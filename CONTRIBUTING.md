# Contributing to NotionForge

NotionForge에 기여해주셔서 감사합니다! 이 문서는 기여 과정을 안내합니다.

---

## 목차

- [개발 환경 설정](#개발-환경-설정)
- [개발 워크플로우](#개발-워크플로우)
- [코드 스타일](#코드-스타일)
- [테스트](#테스트)
- [확장 가이드](#확장-가이드)
- [이슈 & PR 가이드](#이슈--pr-가이드)

---

## 개발 환경 설정

### 사전 요구사항

| 도구 | 최소 버전 | 설치 |
|------|----------|------|
| Python | 3.11+ | [python.org](https://python.org) |
| uv | 최신 | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Node.js | 20+ | [nodejs.org](https://nodejs.org) |
| Docker (선택) | 24+ | [docker.com](https://docker.com) |

### 설치

```bash
git clone https://github.com/JaylenAI/notion_ai_agent.git
cd notion_ai_agent

# Backend
cd backend
uv sync                    # 의존성 설치
cp ../.env.example ../.env # 환경변수 설정 후 값 채우기

# Frontend
cd ../frontend
npm install
```

### 실행

```bash
# 터미널 1: Backend
cd backend
uv run uvicorn app.main:app --port 9500 --reload

# 터미널 2: Frontend
cd frontend
npm run dev
```

### Docker

```bash
docker compose up --build
```

---

## 개발 워크플로우

### 브랜치 전략 (Git Flow 변형)

```
main          ← 안정 릴리스 (태그로 버전 관리, 직접 커밋 금지)
  └── dev     ← 통합 브랜치 (모든 feature가 여기로 머지)
       ├── feature/기능명
       ├── fix/버그명
       └── refactor/대상
```

### 워크플로우

1. **`dev`에서 브랜치 생성**
   ```bash
   git checkout dev && git pull origin dev
   git checkout -b feature/기능명
   ```

2. **개발 + 테스트**
   ```bash
   # 코드 수정 후
   cd backend
   uv run pytest tests/ -v             # 테스트
   uv run ruff check . && uv run ruff format .  # lint + format
   ```

3. **커밋** (컨벤션 메시지)
   ```bash
   git commit -m "feat: 새 기능 설명"
   ```

4. **PR → dev로 머지**

### 커밋 메시지 컨벤션

```
<type>: <설명>

<optional body>
```

| 타입 | 용도 |
|------|------|
| `feat` | 새 기능 |
| `fix` | 버그 수정 |
| `refactor` | 리팩토링 (동작 변경 없음) |
| `docs` | 문서 변경 |
| `test` | 테스트 추가/수정 |
| `chore` | 빌드/도구 설정 |
| `perf` | 성능 개선 |
| `ci` | CI/CD 변경 |

---

## 코드 스타일

### Python (Backend)

- **Formatter**: ruff format (Black 호환)
- **Linter**: ruff check
- 함수: 50줄 이하
- 파일: 800줄 이하 (초과 시 모듈 분할)
- 하드코딩 금지 (환경변수 사용)
- 에러 핸들링 필수
- 타입 힌트 권장

```bash
# 린트 + 포맷 한번에
cd backend
uv run ruff check . --fix && uv run ruff format .
```

### TypeScript (Frontend)

- **ESLint** + TypeScript strict mode
- 컴포넌트: 함수형 + hooks
- 상태관리: Zustand (immutable 패턴)

```bash
cd frontend
npm run lint
npx tsc --noEmit
```

---

## 테스트

### 실행

```bash
cd backend

# 전체 테스트
uv run pytest tests/ -v

# 커버리지
uv run pytest tests/ --cov=app --cov-report=html --cov-fail-under=80

# 특정 파일
uv run pytest tests/unit/test_tool_registry.py -v

# 특정 테스트
uv run pytest tests/unit/test_tool_registry.py::TestToolExecution -v
```

### 테스트 작성 가이드

- 새 기능은 반드시 테스트와 함께 제출
- 최소 80% 커버리지 유지
- async 함수는 `@pytest.mark.asyncio` 데코레이터 사용
- Mock 패턴: `MagicMock`(동기) / `AsyncMock`(비동기)

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_example():
    mock_client = MagicMock()
    mock_client.some_method = AsyncMock(return_value={"id": "123"})
    result = await mock_client.some_method()
    assert result["id"] == "123"
```

자세한 테스트 가이드: [docs/TEST_GUIDE.md](docs/TEST_GUIDE.md)

---

## 확장 가이드

### 새 AI 프로바이더 추가

1. `app/agent/providers/`에 파일 생성
2. `BaseProvider` 상속 + `call()` 메서드 구현
3. `router.py`의 `create_provider()`에 등록
4. 테스트 추가

```python
# app/agent/providers/my_provider.py
from app.agent.providers.base import BaseProvider

class MyProvider(BaseProvider):
    async def call(self, messages, tools=None, **kwargs):
        # LLM API 호출 구현
        ...
```

### 새 도구 (Tool) 추가

1. `app/agent/tools/`에 파일 생성
2. `BaseTool` 상속 + `execute()` 메서드 구현
3. `registry.py`의 `_register_all()`에 등록

```python
# app/agent/tools/my_tool.py
from app.agent.tools.base import BaseTool

class MyTool(BaseTool):
    name = "my_tool"
    description = "도구 설명"
    parameters = {
        "param1": {"type": "string", "description": "설명"},
    }

    async def execute(self, **kwargs):
        return {"result": "success"}
```

### 새 스킬 추가

1. `app/skills/` 아래에 디렉토리 생성 (예: `app/skills/gaming/`)
2. `SKILL.md` 패턴 파일 작성
3. 자동으로 SkillRouter에 감지됨

자세한 스킬 가이드: [docs/SKILL_GUIDE.md](docs/SKILL_GUIDE.md)

### 새 Notion 뷰 타입 추가

1. `app/notion/view_ops.py`에 `create_xxx_view()` 메서드 추가
2. `ViewOpsMixin` 내에 구현
3. 테스트 추가

---

## 이슈 & PR 가이드

### 이슈

- **버그 리포트**: [Bug Report 템플릿](.github/ISSUE_TEMPLATE/bug_report.md) 사용
- **기능 제안**: [Feature Request 템플릿](.github/ISSUE_TEMPLATE/feature_request.md) 사용
- 중복 이슈가 있는지 먼저 검색해주세요

### Pull Request

1. 관련 이슈 번호 연결 (`Closes #123`)
2. 변경 내용 간단 설명
3. 테스트 통과 확인

**PR 제출 전 체크리스트**:

- [ ] `uv run pytest tests/ -v` 전체 통과
- [ ] `uv run ruff check .` lint 통과
- [ ] `uv run ruff format --check .` 포맷 통과
- [ ] 커밋 메시지가 컨벤션을 따르는가?
- [ ] 관련 문서를 업데이트했는가?
- [ ] 새 의존성 추가 시 `pyproject.toml`에 반영했는가?

---

## 질문이 있으면

- [Issues](https://github.com/JaylenAI/notion_ai_agent/issues)에서 질문해주세요
- 버그 리포트는 Issue 템플릿을 사용해주세요
