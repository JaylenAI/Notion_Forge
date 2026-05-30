# 거버넌스 (Governance)

NotionForge의 의사결정·기여·릴리스 운영 방식입니다.

## 역할
- **Maintainer**: 방향 결정, PR 리뷰/머지, 릴리스 책임. 현재 메인테이너는 [MAINTAINERS.md](MAINTAINERS.md) 참고.
- **Contributor**: 이슈/PR로 기여하는 누구나.

## 의사결정
- 일상적 변경: 메인테이너 리뷰 + 머지.
- 큰 변경(아키텍처/破괴적 변경): 이슈 또는 Discussion에서 먼저 논의 → 합의 후 진행. 아키텍처 결정은 `docs/adr/`에 ADR로 기록.

## 브랜치 / 릴리스
- `main`: 안정 릴리스 전용(태그로 버전 관리). `dev`: 통합 브랜치. feature/fix는 `dev`에서 분기 → `dev` 머지.
- 릴리스: `dev` → `main` 머지 + SemVer 태그. CI(release-check)가 버전 일치·테스트·보안 스캔을 검증.
- 버전: `backend/app/__init__.py`(`__version__`)가 단일 출처, `pyproject.toml`·`frontend/package.json`과 일치(CI 강제).

## 기여 흐름
1. 이슈로 논의 → 2. `dev`에서 브랜치 → 3. 테스트(80%+)·린트 통과 → 4. PR(템플릿) → 5. CODEOWNERS 리뷰 → 6. 머지

## 행동 강령
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)를 따릅니다.
