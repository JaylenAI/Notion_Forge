# 진행 현황 (Current Status)

> 최종 업데이트: 2026-06-01
> 현재 브랜치: dev
> 버전: v0.1.6 → **v0.2.0 태그 예정** (버전 bump/태그는 메인테이너 수행)

---

## 0.2.0 — 제품 전 경로 작동 확정 (2026-06-01)

라이브/UI E2E 검증에서 **릴리스 차단급 결함**을 발견·수정해 제품이 UI·AI 파이프라인 전 경로에서 실제로 작동하게 됨. 백엔드 **1,446** + 프론트 Vitest/Playwright E2E(스모크 + 승인→생성) 통과.

- **AI 파이프라인 relation 링크/rollup 집계 복구(CRITICAL)** — 그동안 recipe(결정적) 경로만 검증돼 가려졌던, 실제 제품(AI) 경로의 rollup 미집계 결함 수정. sample relation 다포맷 해석 + single_property 양방향 **미러링**.
- **UI 무생성 함정 제거** — WS 미연결 시 미리보기 전용 폴백을 "성공"처럼 보이게 하던 문제 → 경고 배너 + 정직 안내 + 재연결. 실제 UI(ChatPanel) 승인→Notion 생성 E2E로 보증.
- 차트 x_axis dict 크래시, Groq/OpenAI json 모드 400, AI 무title 영어 기본값, 날짜 dict, 제목 이모지 중복 수정. 미사용 중복 채팅 UI(ChatWindow 체인) 제거.

> **알려진 한계(정직 고지)**: AI 생성은 provider 가용성 의존(Gemini 쿼터 소진 시 copilot/Groq 의존, 동시 실패 시 generic 폴백). AI 샘플 날짜가 과거로 생성될 수 있어 날짜 수식이 음수/큰 값 가능(로직 정상). 단일 워커 권장. 48개 스킬 중 일부 라이브 미검증.

---

## v1.0 하드닝 게이트 (전 게이트 핵심 완료, 1.0 선언은 보류)

실제 Notion 라이브 검증 기반으로 6개 게이트를 진행. 누적 결함 발견·수정 약 40건(라이브 E2E + UI E2E + 멀티에이전트 자기검증), 전부 회귀테스트화. 백엔드 **1,446** + 프론트 vitest/Playwright E2E 통과.

```
Gate 0  공개 전 보안 차단            [██████████] 완료   gitleaks/pre-commit/custom_skills/CI 전체스캔
Gate 1  Agent 안정성 봉합            [██████████] 완료   fallback/approval/cost 실배선 + ADR 0001
Gate 2  템플릿 유료급 품질           [██████████] 완료   rollup 실집계(single_property+샘플링크 미러링)·OKR골든·통화포맷·품질스코어
Gate 3  Notion API 완전성           [██████████] 완료   data_source·페이지네이션·jitter/Retry-After
Gate 4  테스트·관측성·회귀게이트     [█████████░] ~90%   CI 통합테스트·p50/p95·Prometheus·Vitest·Playwright E2E
Gate 5  릴리스·DevOps·공급망         [████████░░] ~80%   버전 SSOT·setup.sh·라이선스 CI·SBOM / cosign·semantic-release 후속
Gate 6  커뮤니티·문서·UX → 공개      [█████████░] ~90%   거버넌스·문서 정직화·예제갤러리·a11y 린트 / a11y 37건 점진개선
```

**라이브 검증 완료**: 자연어 → 실제 AI 생성 → 멀티DB + relation 양방향 링크 + **rollup 실집계(고객별 딜금액 합산, OKR 진행률 평균, 3DB 프로젝트/팀원 집계)** + formula + 통화포맷 + 샘플행, UI 승인→생성 포함 전 과정 실제 Notion에서 동작 확인.

> 1.0+ 후속(선택): cosign 서명, semantic-release, a11y 경고 37건 해소, diff-coverage 도구, provider 가용성 robustness. **버전 태그/릴리스는 메인테이너 수행.**

---

## 전체 진행률 (기능 기준)

```
AI Agent 아키텍처            [██████████] 100%  Plan-Execute-Reflect + Tool Registry 11개
AI Provider 5종              [██████████] 100%  Copilot/Claude/Gemini/Groq/OpenAI
스킬 시스템 48개             [██████████] 100%  12 Tier1 + 36 Tier2
Notion API 듀얼 버전          [██████████] 100%  쓰기 2022-06-28 + 읽기/뷰 2026-03-11
프론트엔드 UI 5페이지        [██████████] 100%  다크/라이트, 반응형, 키보드 단축키
프롬프트 엔지니어링           [██████████] 100%  모듈화 .md 13개 + 골든 예제 8종
블루프린트 자동 수정          [██████████] 100%  PostProcessor 13종 + 구조 검증
보안 미들웨어                [██████████] 100%  Rate Limit, CSRF, 에러 정제, 업로드 검증
CI/CD 파이프라인             [██████████] 100%  lint→test→typecheck→docker→security→api-docs
테스트 1,446개 (80%+ 커버리지) [██████████] 100%  unit 58개 파일, fail_under=80
문서화                       [██████████] 100%  README, CONTRIBUTING, SECURITY, API, ARCHITECTURE
Docker 배포                  [██████████] 100%  Multi-stage, health check, 리소스 제한
오픈소스 배포 준비            [██████████] 100%  MIT, 배너, 이슈 템플릿, Dependabot
```

---

## v0.1.0 주요 기능 (첫 공개 릴리스)

### Phase 1: Notion API 2026-03-11 업그레이드
- API 버전 최신화 (→ 2026-03-11)
- Comments API, File Upload API, Data Sources API 확장
- 듀얼 API 버전 전략: DB/페이지 생성은 2022-06-28 (속성 정상 처리), Views/Workers/쿼리는 2026-03-11

### Phase 2: 13개 기능 확장
- 고급 필터 빌더 (상대 날짜, AND/OR 복합 조건)
- 위젯 빌더 (차트/숫자/리스트 위젯)
- Dashboard 뷰, Form 뷰, View Query API
- DB 쿼리 강화 + 템플릿 지원

### Phase 3: Notion Workers 통합
- Workers API 클라이언트 (Sync/Tool/Webhook CRUD)
- External Agents API (AI 에이전트 네이티브 등록)
- TypeScript scaffold 빌더
- Tool Registry 9→11개 확장

### Phase 4: 오픈소스 배포 준비
- Notion CLI 래퍼
- CI api-docs + release-check 잡
- 문서 전면 개편 (README, CONTRIBUTING, SECURITY)
- 브랜치 26개 정리 → main + dev만 유지

### Phase 5: 안정화 — DB 속성/샘플 데이터 정상화
- Notion API 듀얼 버전 전략 (근본 원인: 2026-03-11이 DB 생성 시 속성 무시)
- `_http_client_legacy` (2022-06-28) 추가 — DB/페이지 생성 전용
- 한국어 동의어 매핑 강화 (30+ 패턴) — 블루프린트 키 → 실제 속성 매칭
- QualityValidator 파이프라인 분리 — 불필요한 재생성 방지, PostProcessor로 자동 수정
- 테스트 1,309 → 1,359개 (+50), 커버리지 80.30%

---

## 아키텍처 개요

```
User Input
  → InputGuardrail (프롬프트 인젝션 방어)
  → IntentAnalyzer (의도 분석 + 레이아웃 라우팅)
  → SkillRouter (키워드 빠른경로 + LLM 정밀경로)
  → BlueprintGenerator (Gen-Eval 구조 검증, 최대 3회)
      → PromptAssembler (base.md + mode + layout + views_catalog)
      → PostProcessor (13종 자동 수정 + 구조 검증)
  → 5-Pass Creation (페이지 → 서브페이지 → DB → 뷰 → 샘플 데이터)
      → Notion API 듀얼 버전 (쓰기: 2022-06-28 / 읽기+뷰: 2026-03-11)
  → Rollback (실패 시 자동 삭제)
```

---

## 기술 스택

| 영역 | 기술 | 버전 |
|------|------|------|
| Backend | Python / FastAPI / uv | 3.11+ / 0.115+ |
| Frontend | React / TypeScript / Vite | 19 / 5.7 / 7 |
| 상태관리 | Zustand | 5 |
| 스타일 | TailwindCSS | 4 |
| AI | Copilot SDK / Claude / Gemini / Groq / OpenAI | Strategy Pattern |
| Notion | notion-client + httpx (듀얼: 2022-06-28 + 2026-03-11) | 2.x |
| 테스트 | pytest / pytest-asyncio / pytest-cov | 80%+ 커버리지 |
| CI/CD | GitHub Actions | lint + test + typecheck + docker + security |
| 배포 | Docker Compose (Multi-stage) | dev/prod |
| 보안 | Rate Limit / CSRF / gitleaks / bandit | |

---

## 테스트 현황

```
테스트 총 수:     1,446개 (+ 라이브 Notion QA 하네스)
커버리지:         80%+ (fail_under=80%)
테스트 파일:      58개+
카테고리:         unit (57+) + integration (1)
```

---

## 프로젝트 구조

```
NotionForge/
├── backend/
│   ├── app/
│   │   ├── agent/              # AI Agent 핵심
│   │   │   ├── orchestrator.py # 오케스트레이터
│   │   │   ├── agent_loop.py   # Plan-Execute-Reflect
│   │   │   ├── providers/      # LLM Provider Strategy (5종)
│   │   │   ├── tools/          # Tool Registry (11개 도구)
│   │   │   └── prompts/        # 모듈화 프롬프트 (.md 13개)
│   │   ├── skills/             # 48개 도메인 스킬
│   │   ├── notion/             # Notion API 클라이언트 (Mixin 패턴)
│   │   │   ├── client.py       # 듀얼 버전 클라이언트
│   │   │   ├── workers.py      # Workers + External Agents API
│   │   │   ├── worker_builder.py # TS scaffold 빌더
│   │   │   ├── filter_builder.py # 고급 필터 빌더
│   │   │   ├── widget_builder.py # 위젯 빌더
│   │   │   └── cli.py          # Notion CLI 래퍼
│   │   ├── routers/            # FastAPI 라우터 (8개)
│   │   ├── core/               # 미들웨어, 로깅, 메트릭스
│   │   └── schemas/            # Pydantic 모델
│   └── tests/                  # 1,446개 테스트
├── frontend/
│   └── src/
│       ├── components/         # React 컴포넌트
│       ├── stores/             # Zustand 상태관리
│       ├── hooks/              # 커스텀 훅
│       └── types/              # TypeScript 타입
├── docs/                       # 문서
├── .github/                    # CI/CD, 이슈 템플릿
├── docker-compose.yml          # 배포 설정
└── CLAUDE.md                   # 프로젝트 규칙
```
