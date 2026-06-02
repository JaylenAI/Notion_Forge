# 진행 현황 (Current Status)

> 최종 업데이트: 2026-06-02
> 현재 브랜치: dev=main (v0.2.0 릴리스 — v1.0 완성 플랜 6 Phase 반영)
> 버전: **v0.2.0** (유료급 품질 대규모 업그레이드 — 2026-06-02)

---

## Track 2 "유료급 품질" — 진행 중 (2026-06-02~)

산출물을 **$20-49 마켓플레이스 품질 바**로 끌어올리는 로드맵(A1~A5 품질 → B1~B2 채팅 E2E → C 완벽화). OSS·DB/과금 없음.

- ✅ **Phase A1 — 품질 측정 인프라** (2026-06-02)
  - 유료급 루브릭(0~100 + 가격 밴드) + LLM 주관 심사(PASS/FAIL) + 통합 리포트(**비차단 측정**) + 전체 blueprint 로컬 저장(error analysis용).
  - baseline: golden/recipe 측정 → 멀티DB $50-99, 단순 레이아웃 $5-15. 라이브: Gemini judge CRM 5/5 PASS.
- ✅ **Phase A2 — 셀러빌리티 레이어** (2026-06-02)
  - 온보딩 "시작하기" 페이지 + 상단 네비 + 목차 자동 주입(멱등) + 리스팅 키트 생성.
  - 실데이터: golden 평균 **53.6→60.1(+6.5)**, flagship **88→92($100+)**. 라이브 "독서 트래커" **44.6→51.2**. 백엔드 **1,505** 테스트(신규 13)·ruff clean.
- ✅ **Phase A3 — 시각 프리미엄** (2026-06-02)
  - 뷰 큐레이션(속성→board/calendar 자동, 멱등) + 아이콘 보강(키워드 인지). view_ops·creation_executor는 완비 — 생성기가 풍부한 뷰를 채우게 함.
  - 실데이터: golden 뷰 큐레이션 작동(dashboard +3뷰 등), 라이브 "프로젝트 대시보드" DB아이콘✅·table/board/calendar. 백엔드 **1,513** 테스트(신규 8)·ruff clean.
- ✅ **Phase A4 — 품질 게이트 + 결정성** (2026-06-02)
  - `premium_ready` 판정 + 미달 사유 고지(`quality_gate_enabled`) + blueprint pin(byte-stable 재생성). 실데이터 QA로 QualityValidator title false-positive(게이트 차단급) 발견·수정.
  - 게이트 검증: 프리미엄(92/86/84) ✅통과 / 단순($40-57) ❌차단. 백엔드 **1,521** 테스트·ruff clean.
- ✅ **Phase A5 — 도메인 예시 검색·주입** (2026-06-02)
  - 고품질 recipe를 예시 코퍼스로, 도메인 키워드(한국어 포함) 매칭 → 멀티DB 예시를 생성 프롬프트에 주입. **벡터 RAG 아님**(golden few-shot 확장, 무DB).
  - 라이브: "고객 관리 영업 시스템" → 실제 AI 3DB·relation 2개, **70.4 ($20-49) premium_ready=True**. 백엔드 **1,529** 테스트.
- 🏁 **축A(유료급 품질) 전체 완료** (A1~A5) — 측정→셀러빌리티→시각→게이트→예시주입
- ✅ **Phase 1 — 엔진 품질 마무리** (judge→repair, 2026-06-02): judge FAIL→약점 피드백→1회 재생성→더 나은 것 채택(evaluator-optimizer 완성). 단위 5종·**1,534** green.
- ✅ **Phase 2 — 가치 가시화 + 정직성** (2026-06-02): QualityPanel(품질 등급·판매준비·점수·리스팅 초안 표시) + StatusBar 가짜 텔레메트리 제거 + ProfilePage 정적스킬→`/api/skills` 동적. 프론트 tsc/build/lint·vitest 6 통과. (토큰메트릭 정직화는 C1에서 실측 배선)
- ✅ **E2E 품질 보정** (2026-06-02): 실제 Notion E2E에서 발견한 generic DB명·status 옵션 400·하네스 한계 수정. DB명 유추(고객/거래), status 옵션 객체화, **하네스가 rollup 집계값까지 검증**(재확인: 총거래액 [₩2.5M,2M,3M,9M] 실집계). 1,540 green. **QA 기준 = 실제 Notion 생성+rollup값 확인.**
- ✅ **Phase 3 — B1 AI 대화형 수정 (1차)** (2026-06-02): LLM 분류기(자유 발화→올바른 핸들러, regex 폴백) + recolor("색 바꿔줘" 라이브 변경). **실 Notion E2E: 보라색 recolor 4/4 블록 확인** + rich_text 누락 400 수정. 1,547 green. (후속: op별 LLM 파라미터 추출·구조화 diff)
- ✅ **Phase 4 — B2 캔버스 UX (1차)** (2026-06-02): 버전 히스토리/롤백(`VersionRail` — 세션 내 blueprint 리비전을 v1·v2·최신 칩으로 열람). 2-pane 프리뷰는 기존. 프론트 tsc/build·lint 0err·vitest 9. (후속: 스코프드 편집·점진 채워짐)
- ✅ **Phase 5 — C1 비용 + C2 평가 (1차)** (2026-06-02): 토큰 집계 실측(provider usage→note_tokens→metrics.finish, /metrics 0→실측, **라이브 4,706토큰**) + 품질 회귀 게이트(recipe 밴드 미달 시 CI 실패). 1,555 green. (후속: 모델 라우팅·캐싱, 프론트 jsdom·라이브 Notion 회귀 CI)
- ✅ **Phase 6 — C3 위생·정직화** (2026-06-02): 死코드 7파일 제거(`skill_matcher`+프론트 5종)·하드코딩 4 봉합·README 정직화(Gen-Eval+judge로 정정)·.env.example 보강. 백엔드 1,545·프론트 build green.
- 🏁 **v1.0 코드 6 Phase 전부 완료.** 남은 건 **릴리스(버전 bump/dev→main/태그/push) — 사용자 결정.**
- 잔여 확장(선택, v1.0+): B1 파라미터 추출, B2 스코프드 편집, C1 모델 라우팅·캐싱, C2 jsdom·라이브 Notion 회귀 CI.

---

## 0.1.7 — 제품 전 경로 작동 확정 (2026-06-01)

라이브/UI E2E 검증에서 **릴리스 차단급 결함**을 발견·수정해 제품이 UI·AI 파이프라인 전 경로에서 실제로 작동하게 됨. 백엔드 **1,461** + 프론트 Vitest/Playwright E2E(스모크 + 승인→생성) 통과.

- **AI 파이프라인 relation 링크/rollup 집계 복구(CRITICAL)** — 그동안 recipe(결정적) 경로만 검증돼 가려졌던, 실제 제품(AI) 경로의 rollup 미집계 결함 수정. sample relation 다포맷 해석 + single_property 양방향 **미러링**.
- **UI 무생성 함정 제거** — WS 미연결 시 미리보기 전용 폴백을 "성공"처럼 보이게 하던 문제 → 경고 배너 + 정직 안내 + 재연결. 실제 UI(ChatPanel) 승인→Notion 생성 E2E로 보증.
- 차트 x_axis dict 크래시, Groq/OpenAI json 모드 400, AI 무title 영어 기본값, 날짜 dict, 제목 이모지 중복 수정. 미사용 중복 채팅 UI(ChatWindow 체인) 제거.
- **provider 폴백 신뢰성(CRITICAL)** — copilot 빈응답을 '성공'처리해 폴백을 건너뛰던 결함 → 유효 응답만 성공으로 보고 copilot→groq→gemini→claude 캐스케이드. circuit-aware(429 차단 건너뜀)+groq 우선. 전 provider 실패 시 generic 폴백 사용을 명확히 고지.
- **결정적 recipe 검증(쉬움→복잡 4종)** — reading/project/CRM/OKR 전부 rollup 집계·formula 계산·relation 양방향·샘플데이터 정상. CRM '남은일수' formula 미계산(딜 샘플 날짜 누락) 수정.

> **알려진 한계(정직 고지)**: AI 생성은 provider 가용성 의존(Gemini 쿼터 소진 시 copilot/Groq 의존, 동시 실패 시 generic 폴백으로 graceful degradation + 고지). AI 샘플 날짜가 과거로 생성될 수 있어 날짜 수식이 음수/큰 값 가능(로직 정상). 단일 워커 권장. 48개 스킬 중 일부 라이브 미검증.

> **하드코딩 아님**: 자연어 입력의 정상 경로는 LLM이 전 구조(blocks·DB·relation·rollup·formula·샘플)를 자유 설계(ai_dynamic). 하드코딩은 (a) 전 provider 실패 시 비상 폴백(smart_fallback, 8종) (b) 큐레이션 예제 갤러리(recipes)뿐.

---

## v1.0 하드닝 게이트 (전 게이트 핵심 완료, 1.0 선언은 보류)

실제 Notion 라이브 검증 기반으로 6개 게이트를 진행. 누적 결함 발견·수정 약 40건(라이브 E2E + UI E2E + 멀티에이전트 자기검증), 전부 회귀테스트화. 백엔드 **1,461** + 프론트 vitest/Playwright E2E 통과.

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
테스트 1,461개 (80%+ 커버리지) [██████████] 100%  unit 58개 파일, fail_under=80
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
테스트 총 수:     1,461개 (+ 라이브 Notion QA 하네스)
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
│   └── tests/                  # 1,461개 테스트
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
