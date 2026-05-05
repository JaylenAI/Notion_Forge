# Release Checklist

새 버전 릴리스 전 확인 사항.

---

## 코드 품질

- [ ] `cd backend && uv run pytest tests/ -v` — 전체 테스트 통과
- [ ] `cd backend && uv run pytest tests/ --cov=app --cov-fail-under=80` — 커버리지 80%+
- [ ] `cd backend && uv run ruff check . && uv run ruff format --check .` — 린트 통과
- [ ] `cd frontend && npx tsc --noEmit` — TypeScript 타입 체크 통과
- [ ] `cd frontend && npm run lint` — ESLint 통과
- [ ] `cd frontend && npm run build` — 프론트엔드 빌드 성공

## 보안

- [ ] `.env` 파일이 `.gitignore`에 포함
- [ ] 코드에 하드코딩된 시크릿 없음 (`grep -rn "sk-\|ntn_\|gsk_" backend/app/`)
- [ ] `pip-audit` 취약점 없음
- [ ] Rate Limiting 활성화 확인
- [ ] 에러 메시지에 스택 트레이스 노출 없음

## Docker

- [ ] `docker compose build` — 이미지 빌드 성공
- [ ] `docker compose up` — 정상 시작
- [ ] `curl http://localhost:9500/health` — 200 OK
- [ ] `curl http://localhost:9500/health/ready` — ready: true

## 문서

- [ ] `README.md` 버전 번호 업데이트
- [ ] `docs/CHANGELOG.md` 업데이트
- [ ] `docs/CURRENT_STATUS.md` 업데이트
- [ ] `.env.example` 새 환경변수 반영

## 버전 동기화

- [ ] `backend/app/main.py` — version 필드
- [ ] `backend/pyproject.toml` — version 필드
- [ ] `frontend/package.json` — version 필드
- [ ] `README.md` — 버전 표기

## 릴리스 실행

```bash
# 1. dev 브랜치 최신 확인
git checkout dev && git pull origin dev

# 2. main으로 머지
git checkout main && git merge dev

# 3. 태그 생성
git tag -a v9.0.0 -m "v9.0.0: 오픈소스 릴리스"

# 4. 푸시
git push origin main --tags

# 5. GitHub Release 작성 (release.yml 자동 트리거)
```

## 릴리스 후 확인

- [ ] GitHub Actions release.yml 성공
- [ ] Docker 이미지 ghcr.io 배포 확인
- [ ] GitHub Release 페이지에 changelog 표시
- [ ] README 뱃지 정상 렌더링
