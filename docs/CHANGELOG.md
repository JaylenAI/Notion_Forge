# 변경 이력 (Changelog)

> 주요 변경사항 기록. [Keep a Changelog](https://keepachangelog.com) 형식 준수.

---

## [8.2.0] - 2026-05-15

### Added (Notion API 2026-03-11 전면 업그레이드 + Workers 통합)

**Phase 1: API 최신화**
- Notion API 버전 2026-03-11로 업그레이드 (최신)
- Comments API: 생성/조회/수정/삭제 + 스레드 댓글
- File Upload API: 서버→Notion 직접 파일 업로드
- Data Sources API: 외부 데이터소스 연동 인프라
- 레거시 호환 코드 제거

**Phase 2: 13개 기능 확장**
- 고급 필터 빌더 (`filter_builder.py`): 상대 날짜, multi-value, "me" 필터, AND/OR 복합 조건
- 위젯 빌더 (`widget_builder.py`): 차트/숫자/리스트/필터뷰 위젯 + 대시보드 배치
- Dashboard 뷰 생성 (`create_dashboard_view`): 위젯 기반 대시보드
- Form 뷰 생성 (`create_form_view`): 제출 권한 설정 (disabled/anyone/workspace)
- View Query API (`create_view_query`): 뷰에 필터/정렬 쿼리 바인딩
- 번호 리스트 확장: 숫자/알파벳/로마자 포맷 + 시작 인덱스
- DB 쿼리 강화: `filter_properties` 지원 + 불완전 결과 처리
- 페이지 생성 시 `template_id` 파라미터 지원

**Phase 3: Notion Workers 통합**
- Workers API 클라이언트 (`workers.py`): Sync/Tool/Webhook 워커 CRUD + 로그 조회
- External Agents API (`workers.py`): AI 에이전트 Notion 네이티브 등록/관리
- TypeScript scaffold 빌더 (`worker_builder.py`): 실행 가능한 TS 코드 + 프로젝트 구조 자동 생성
- `CreateWorkerTool`: Agent Loop에서 워커 생성 도구
- `RegisterAgentTool`: Agent Loop에서 에이전트 등록 도구
- Tool Registry 9→11개 확장

**Phase 4: 오픈소스 배포 준비**
- Notion CLI 래퍼 (`cli.py`): `ntn` CLI를 Python에서 비동기 실행
- CI `api-docs` 잡: dev/main 푸시 시 OpenAPI 스키마 자동 생성
- CI `release-check` 잡: main 전용 — 테스트 수, TODO/FIXME, 버전 일관성 검증
- 테스트 1,309개 (1,215 → 1,309, +94)

### Changed
- README 전면 개편: Hermes Agent 수준 오픈소스 문서 구조
- CONTRIBUTING.md: 확장 가이드 (프로바이더/도구/스킬/뷰) 추가
- SECURITY.md: GitHub URL 업데이트
- GitHub 리포지토리 URL: `JaylenAI/notion_ai_agent`로 통일
- 머지 완료된 feature 브랜치 26개 정리 (→ main + dev만 유지)

---

## [8.1.0] - 2026-05-13

### Added (오픈소스 배포 준비 + 보안 강화)
- **Rate Limiting 미들웨어**: IP 기반 슬라이딩 윈도우 (기본 60 req/min, `RATE_LIMIT_RPM` 환경변수)
- **Request ID 추적**: `X-Request-ID` 헤더 자동 주입/전파 (디버깅 용도)
- **OAuth CSRF 방어**: `secrets.token_urlsafe` 기반 state 파라미터 + 5분 TTL
- **WebSocket 보안 강화**: 10초 init 타임아웃, 토큰 검증, 20 msg/min 레이트리밋
- **에러 메시지 정제**: 프로덕션 환경 스택트레이스 은닉 (`sanitize_error()`)
- **파일 업로드 검증**: 10MB 제한 + 확장자 화이트리스트 (txt/md/csv/pdf)
- **GitHub Actions CI**: ruff lint → pytest 80% → TypeScript → Docker → gitleaks + bandit
- **보안 문서**: SECURITY.md, DEPLOYMENT.md, RELEASE_CHECKLIST.md
- **프론트엔드 문서**: frontend/README.md (기술 스택, 빠른 시작, 프로젝트 구조)
- **테스트 대폭 확장**: 1215개 테스트, 82% 커버리지 달성
  - 신규: providers, database_ops, middleware, oauth, workspace, ai_router,
    chat_router, template_router, copilot_client, notion_ops, agent_tools 등 14개 파일

### Changed
- **AI 라우터**: 글로벌 설정 변경 → 세션 스코프 모델 관리로 전환
- **Coverage 기준**: `fail_under` 60% → 80%으로 상향
- **README**: CI/License/Python/Docker 뱃지 추가

### Fixed
- **post_processor**: view가 문자열인 경우 `view.get()` 호출 시 AttributeError
- **WebSocket**: 동시성 버그 수정 (Approval Gate)
- **DB 속성 키 호환**: REST API Approval Gate 자동승인

### Security
- OAuth 콜백 state 검증 (CSRF 방어)
- 프로덕션 에러 응답에서 민감 정보 제거
- WebSocket 인증 강화 (최소 5자 토큰)
- gitleaks + bandit 자동 보안 스캔 CI 통합

---

## [8.0.0] - 2026-04-24

### Added (엔터프라이즈급 AI Agent)
- Plan-Execute-Reflect Agent Loop: AI가 도구 직접 선택·실행·검증 (최대 3회 Re-plan)
- Tool Registry 9개 도구: create_view 추가 (Agent Loop에서 뷰 프로그래밍 생성)
- 하이브리드 SkillRouter: 키워드 빠른경로 (score≥2) + LLM 정밀 분류
- Episodic Memory: 성공/실패 패턴 학습 + 유저 선호도 기억 + AI 컨텍스트 주입
- 버튼 블록 지원: Notion 자동화 트리거 (block_builder.button)
- Memory REST API: GET/POST /memory/preferences, GET /memory/stats
- MIT LICENSE 추가 (오픈소스 배포 준비)
- 테스트 95개 추가 (151→246): provider_router, tool_registry, agent_loop, skill_router, memory

### Changed
- Provider Strategy 통합: 6개 프로바이더를 ProviderRouter로 자동 라우팅
- blueprint_generator: skill_router 모듈로 스킬 매칭 분리
- 보안 강화 5건: Path Traversal (recipes), OAuth 토큰 fragment 전달, ID UUID 검증, Pydantic Field 제약, API 키 max_length

### Fixed
- OAuth 토큰 노출: 쿼리 파라미터 → URL fragment 전달로 변경
- 통합 테스트: Pydantic 검증 강화에 맞춰 테스트 기대값 수정

---

## [7.5.0] - 2026-04-18

### Added (스킬 확장 + 품질 마무리)
- 48개 스킬 확장: 11개 Tier2 추가 (onboarding, wiki, sop, team_home, life_os, diary, gratitude, review, blog, youtube, social)
- 커버 이미지 75개: 25 카테고리 x 3장 (기존 20개에서 대폭 확장)
- WebSocket 자동 재연결: 연결 끊김 감지 + 자동 복구
- NotionClient.close(): httpx 세션 리소스 정리

### Changed
- print→logger 전환: 11개소 구조화 로깅으로 교체
- OAuth FRONTEND_URL 환경변수: 하드코딩 URL 제거
- docker-compose.dev 포트 수정
- 보안 강화: API 에러 응답에서 상세 정보 제거
- blueprint_generator 분할: 781→563줄 (creation_executor로 분리)
- creation 로직 통합: orchestrator에서 creation_executor로 이동
- modify_handler 디스패치: 수정 로직 별도 모듈로 분리
- 라우터 분할: template.py → template.py + ai.py + workspace.py (3개)
- chatStore 분할: 610→260줄 (connectionStore + settingsStore 분리)

---

## [7.4.0] - 2026-04-16

### Added (코드 품질 + 테스트 강화)
- God Object 분해: orchestrator.py에서 4개 모듈 추출 (creation_executor, modify_handler, view_builder, skill_matcher)
- Provider Strategy 패턴: agent/providers/ 디렉토리 (base, router, copilot/claude/gemini/groq/openai)
- Pydantic 스키마 정비: schemas/blueprint.py, chat.py, template.py
- 테스트 151개: 71→151 (view_builder, metrics_history, skill_matching, input_guardrail 등 추가)
- Path traversal 방어: 스킬 파일 경로 검증

### Fixed
- DB property key 호환: 속성 키 불일치 수정
- REST Approval Gate: auto-approve 모드 추가 (REST API 호출 시)

---

## [7.3.0] - 2026-04-14

### Added (안전성 + 관측성)
- Input Guardrail: 프롬프트 인젝션 방어 + 입력 길이/형식 검증
- Approval Gate: 생성 전 "DB 3개 생성합니다. 진행할까요?" 사용자 확인/취소
- Rollback: Notion 생성 실패 시 이미 생성된 페이지/DB 자동 삭제
- Structured JSON Logging: logging_config.py 구조화 로깅
- Metrics 저장: 토큰 사용량, 소요시간, 재시도 횟수 기록
- History 저장: 생성 이력 영속 저장 + 조회 API
- 스킬 48개 확장: 37→48 (guide/hub/journal/content 하위 스킬)
- AI 대화 히스토리: 멀티턴 컨텍스트 전달
- 실패 시 전략 변경: 복잡 템플릿 실패 → 간소화 재시도
- Approval Gate UI: 채팅에서 확인/취소 버튼
- 모델 퀵 디스플레이: 채팅 하단에 현재 모델 표시
- CONTRIBUTING.md: 기여 가이드
- Docker 볼륨: 이력 데이터 영속화

---

## [7.2.0] - 2026-04-12

### Added (프로 템플릿 + 스킬 확장)
- 골든 블루프린트 8개: 레이아웃별 검증된 완성 JSON Few-Shot 예시
- 스킬 세분화 37개: 12개 범용 → 25개 도메인 특화 추가 (fitness, reading, budget 등)
- 2-Tier 스킬 매칭: 세분화 스킬(Tier 2) 우선 → 범용 카테고리(Tier 1) 폴백
- Post-Creation Validation: Notion 생성 후 실제 결과 검증 (블록/DB/서브페이지 수 비교)
- PromptAssembler Few-Shot: 골든 블루프린트를 compact 프롬프트에 자동 삽입

---

## [7.1.0] - 2026-04-12

### Added (하네스 고도화 + 프로 템플릿 품질)
- Nesting 패턴: callout/toggle/heading children 사용법 + JSON 예시 (base.md)
- 레이아웃 8종에 완성된 JSON blocks[] 예시 추가
- 스킬 12개 핵심 패턴 추출 (15줄 잘림 → 핵심 섹션 자동 추출)
- link_to_page 동적 주입: `sub_page_ref` 플레이스홀더 → ID 치환
- DB 배치 전략: `db_parent` 필드로 서브페이지에 DB 생성 + 메인에 linked_view
- 2-Stage 파이프라인: advanced 모드에서 자동 활성화 (Architect→Designer→Content→Validator)
- Model Escalation: GPT-4.1 실패 → GPT-5.2 → GPT-5 Mini 자동 업그레이드

---

## [7.0.0] - 2026-04-10

### Added (하네스 엔지니어링)
- Copilot SDK 연동: GPT-4.1 등 7개 모델, API 키 불필요 (GitHub Copilot 구독)
- 프롬프트 모듈화: prompts/*.md 13개 파일 동적 조립
- Intent Router: 8개 레이아웃 자동 매핑 (simple_tracker, gallery_hero, kanban_board 등)
- 레이아웃 프롬프트 8종: 각각 고유한 블록 배치 패턴
- Gen-Eval 피드백 루프: 구조 검증 실패 → AI에게 에러 피드백 → 재생성 (최대 3회)
- Post-processor: 7개 규칙 자동 보정 (callout 누락, status 매핑, spacing)
- Circuit Breaker: 최대 재시도 초과 시 최선 결과 사용
- Copilot 모델 선택 UI: Integrations 페이지
- 테스트 71/71: 하네스 32개 포함

---

## [6.0.0] - 2026-04-08

### Added (v6 대규모 업데이트)
- Relation + Rollup + Formula 자동 생성
- 멀티턴 대화형 수정 (속성/뷰/DB/Relation/Formula/서브페이지/블록)
- 복잡도/언어 선택 UI (Simple/Standard/Advanced + KR/EN/JP)
- Blueprint JSON Export/Import
- 커뮤니티 레시피 갤러리 (recipes/ + API + UI)
- 다국어 지원 (한/영/일)
- 멀티 에이전트 파이프라인 (Architect→Designer→Content→Validator)
- Document-to-Notion (CSV/MD/TXT/PDF)
- OAuth 연동 (Notion OAuth 플로우)
- 디자인 토큰 시스템, 혼합 리치텍스트, 서브페이지 AI 패스스루
- 커스텀 스킬 CRUD API + UI

---

## [5.4.0] - 2026-04-06

### Added (28개 미구현 기능 추가 + 복잡도 스케일링)
- DB description/icon/cover 파라미터 (create_database)
- 뷰 group_by, sub_group_by, quick_filters, properties, position 파라미터 (create_view)
- 블록 레벨 코멘트 (block_id), 답글 스레드 (discussion_id)
- 페이지 이동 API (move_page — 부모 변경, 2026-01-15+)
- 마크다운 콘텐츠 교체 (update_page_content_markdown, 2026-03-11+)
- linked_view 블록 타입 (필터된 DB뷰를 대시보드 위젯으로 활용)
- 복잡도 3단계 스케일링 (simple 10-15 / medium 15-25 / complex 25-40 블록)
- 3컬럼 대시보드 레이아웃 패턴 (위젯 그리드 + toggle 네비게이션)
- Pattern C: Complex Dashboard (3col widgets + 3col toggle nav + 3-4 DB)
- Groq TPM 제한 대응 (스킬 가이드 축약)

---

## [5.3.0] - 2026-04-02

### Added
- 블록 position API 지원 (after_block, page_end — 블록 삽입 위치 제어)
- 서브페이지 하단 배치 (position: page_end)
- 실시간 progress 로그 스트림 (채팅에서 생성 과정 실시간 표시)
- 서브페이지 내용 자동 생성 (빈 페이지 방지)
- 블록 다양성 강제 규칙 (quote/to_do/numbered_list 최소 3개)
- Status 매핑 50+ 패턴 (독서/학습/콘텐츠/영어)
- DB title 속성 자동 보장 (build_database_properties)

### Fixed
- 미리보기 ≠ 실제 노션 불일치 해결 (column 안 database_ref 금지 규칙)
- 샘플 데이터 status 에러 (한국어→영어 자동 매핑)
- WebSocket 연결 끊김 (progress 이벤트 분리, ErrorBoundary 복구)
- 한글 IME 입력 잔여 글자 (isComposing 체크)
- 이모지 유효성 에러 자동 폴백
- column_list 파싱 (list/dict 양방향 지원)
- toggle children 필수 보장

### Changed
- Library 저장: 자동 → 수동 (Save to Library 버튼)
- 사이드바: PRO PLAN 제거, Support → nav 항목 이동
- column 안에 database_ref 금지 → 미리보기=실제 100% 일치

---

## [5.2.0] - 2026-04-01

### Changed
- Library 저장 방식: 자동 저장 → 수동 저장 (Save to Library 버튼)
- 이미 저장된 템플릿은 "Saved" 상태로 비활성화 + 중복 방지
- 사이드바: PRO PLAN 카드 제거
- 사이드바: Support를 nav 항목으로 이동 (Profile 아래)

---

## [5.1.0] - 2026-04-01

### Added (AI 프로 디자인 + Notion 확장 기능)
- AI 시스템 프롬프트 전면 재작성 (Thomas Frank/Easlo 수준 디자인 규칙 50+개)
- 색상 팔레트 2-3색 제한 규칙 (스킬별 추천 팔레트 7종)
- 대시보드 컬럼 30/70 분할 필수화 (column width_ratio API 지원)
- 정보 계층 구조 강제 + 아마추어 안티패턴 10가지 방지
- DB 뷰-속성 자동 매칭 규칙 (status→board, date→calendar)
- 커버 이미지 10→20개 확장 (카테고리별: business/fitness/study/finance 등)
- 12개 스킬 전체에 Pro Design Guide 섹션 추가
- 페이지 전체 너비 자동 설정 (Notion Internal API submitTransaction + token_v2)
- 링크드 DB 뷰 생성 (공식 Views API create_database 파라미터)
- 컬럼 width_ratio 지원 (block_builder + orchestrator)
- NOTION_TOKEN_V2 환경변수 + .env.example 가이드

### Fixed
- 미리보기 패널 오버플로우 (블루프린트 렌더링 시 툴바 밀림)
- 채팅 메시지 하단 정렬 (빈 공간 상단으로)
- LivePreview 툴바 줄바꿈 방지 (whitespace-nowrap)

---

## [5.0.0] - 2026-04-01

### Added (프론트엔드 UI/UX 대규모 고도화)
- 채팅 메시지 마크다운 렌더링 (react-markdown + remark-gfm)
- 메시지 타임스탬프 (hover 시 "3분 전" 한글 상대시간)
- 채팅 히스토리 세션 관리 (자동저장/복원, 최대 50개, 삭제)
- 다크/라이트 모드 토글 (CSS 변수 기반 전체 테마 시스템)
- 모바일 반응형 레이아웃 (768px 이하: 탭 전환, 오버레이 사이드바)
- 키보드 단축키 (Cmd+N 새 템플릿, Cmd+K 커맨드 팔레트)
- 커맨드 팔레트 (검색 + 네비게이션 + 단축키 힌트)
- 생성 중 취소 버튼 (AbortController + WebSocket cancel 메시지)
- 토스트 알림 시스템 (react-hot-toast — 저장/연결/에러/복사 피드백)
- 미리보기 줌 인/아웃 (50%~150%, 5단계, 리셋 버튼)
- Notion URL 복사 버튼 (클립보드 복사 + 토스트 확인)
- 프롬프트 템플릿 라이브러리 (Business/Personal/Content/Learning 4개 카테고리, 18개 프롬프트)
- 테마 스토어 (Zustand + localStorage 영속)
- 상대시간 유틸리티 (lib/timeago.ts)

### Changed
- 커스텀 리사이저블 패널로 교체 (react-resizable-panels 라이브러리 제거 → 순수 CSS+mouseEvent 구현, localStorage 캐시 문제 근본 해결)
- StatusBar 사이드바 오프셋 적용 (사이드바에 가려지지 않도록 left 동적 계산)
- 사이드바 footer에 pb-14 적용 (StatusBar 겹침 방지)
- 사이드바 CSS를 인라인 style로 전환 (Tailwind 클래스 충돌 해결)
- LivePreview 툴바 줄바꿈 방지 (whitespace-nowrap + lg breakpoint 반응형)
- 채팅 입력란에 프롬프트 라이브러리 버튼 추가

### Removed
- react-resizable-panels 패키지 의존성 제거

---

## [4.0.0] - 2026-04-01

### Added (스킬 확장 + 프론트엔드 고도화)
- 새 스킬 5개 추가 (finance, journal, content, learn, crm) → 총 12개
- 기존 스킬 7개 개선 (컬러 테마 가이드, 복잡도 레벨, 크로스 스킬 조합)
- 프롬프트 스타터 카드 6개 (원클릭 생성)
- NotionRenderer 블록 추가: quote, code, numbered_list, bookmark
- NotionRenderer DB 뷰 분기: Board(칸반), Calendar(월간), Gallery(카드)
- Library 자동 저장 (생성 완료 시 localStorage에 자동 보관)
- Library 검색/스킬별 필터/4종 정렬 (최신/오래된/이름/즐겨찾기)
- 완료 후 액션 버튼 (Open in Notion + Create Another)
- 에러 상태 UI (빨간 아이콘 + Error 라벨)
- Progress 단계별 아이콘 표시
- Profile 페이지: 실제 연결 상태 + 템플릿 수 표시 (Mock 제거)
- 폴백 템플릿 3개 → 6개 (가계부, 일기장, 콘텐츠 캘린더 추가)
- 영어 키워드 폴백 매핑 (workout, budget, journal 등)
- Status 색상 매핑 (시작전/진행중/완료)

### Changed
- UI 전체 영어 통일 (Integrations, LivePreview, AppLayout 한글→영어)
- Profile 페이지: Mock 통계 제거 → 실제 데이터 연동
- Integrations: Quick Actions 비기능 카드 제거
- Library: Mock 템플릿 4개 제거 → 실제 생성 이력 기반
- ModelBadge: 이모지 → 텍스트 약자 (G/A/O)
- Support: GitHub URL 실제 레포로 수정

### 테스트 현황: 39/39 통과 | Notion 실제 생성 QA 8건 성공

---

## [0.4.0] - 2026-03-29

### Added (프로덕션 준비)
- Integration Tests 10개 (health, patterns, preview, generate, search, 404)
- 전역 Exception Handler (500 JSON 응답)
- HTTP 요청 로깅 미들웨어 (method, path, status, duration)
- Notion Client 에러 래핑 (create_page, create_database, add_blocks, add_database_item)
- Health Check 고도화 (version, ai_provider, notion_ready, features)
- 구조화된 로깅 (timestamps, level)
- Docker healthcheck + non-root user + 리소스 제한
- Makefile: test-all, typecheck 추가
- .env.example: GROQ_API_KEY, GEMINI_API_KEY 추가

### 테스트 현황: 38/38 통과 (28 unit + 10 integration)

---

## [3.1.0] - 2026-04-01

### Added
- 실시간 스트리밍: 템플릿 생성 과정을 단계별로 실시간 표시
  (의도 분석 → 설계 → 페이지 생성 → DB 생성 → 샘플 추가 → 뷰 추가 → 완료)
- 시스템 프롬프트 대폭 개선: 다양한 블록 조합 강제 규칙 14개
  (column_list, to_do, quote, toggle, numbered_list 등 적극 활용)

### Changed
- AI 자유 설계: 하드코딩 빌더 7개 삭제 → AI가 blocks[] 직접 생성
- max_tokens: 2048 → 4096 (복잡한 템플릿 지원)

---

## [3.0.0] - 2026-04-01

### Changed (핵심: AI 자유 설계)
- 하드코딩 빌더 7개 함수 삭제 (_build_track, _build_collect 등)
- AI가 blocks[] 배열도 직접 생성 → 유저 요청 복잡도에 비례하는 결과
- 기본 Gemini 모델: gemini-2.0-flash → gemini-2.5-flash

### Added
- AI 모델 선택 UI (Integrations 페이지)
- 프로바이더 자동 감지 (키 접두사) + 모델 목록 API 조회
- 4개 프로바이더 지원 (Gemini/Groq/Claude/OpenAI)
- 채팅 헤더에 현재 모델 배지
- AI 우선순위: Claude > Gemini > Groq > Mock
- OpenAI 프로바이더 추가
- 노션 스타일 렌더러 (NotionRenderer.tsx)
- Profile/Support 페이지, 상단 아이콘, 로고 홈 이동

### Fixed
- DB 400 에러: TYPE_ALIASES 17개 별칭
- Gemini 2.0-flash 할당량 0 → 2.5-flash로 변경

---

## [2.0.0] - 2026-03-30

### Added (프론트엔드 전면 리뉴얼)
- 레퍼런스 #1 다크 테마 UI (5개 페이지)
- 노션 스타일 렌더러 (callout, heading, DB 테이블, 뷰 탭, 체크리스트, 토글)
- PREVIEW 토글, Profile/Support 페이지, 상단 아이콘, 로고 홈 이동

### Fixed
- DB 400 에러: TYPE_ALIASES 17개 별칭 (text→rich_text, person→rich_text 등)
- Select 옵션 색상 검증, 채팅 overflow, 미리보기 색감 통일

---

## [1.1.0] - 2026-03-30

### Fixed
- 시스템 프롬프트 이스케이프 버그 ({} → {{}} Python .format 충돌)
- AI 실패 시 재시도 로직 추가 (최대 2회)

### Improved
- 시스템 프롬프트 완전 개선 (구체적 예시 포함, AI 성공률 향상)
- 스마트 폴백 시스템 (5개 맥락별 기본 템플릿: 운동/독서/프로젝트/일정/대시보드)
- 폴백도 속성 5~7개 + 샘플 5개 + 뷰 2~3개 보장 (기존: 항목1,2,3)

---

## [1.0.0] - 2026-03-30

### Fixed (핵심 버그)
- DB 속성 미생성 → Legacy API (2022-06-28) 사용으로 해결
- 샘플 데이터 미삽입 → DB 조회 + 항목 삽입 모두 Legacy API로 전환
- 원인: notion-client SDK 3.0 (2025-09-03)에서 properties 빈 객체 반환

### Added
- 스킬 개발 가이드 (docs/SKILL_GUIDE.md)
- 시스템 프롬프트 샘플 데이터 필수 규칙 (BAD/GOOD 예시)
- 스킬 자동 발견 (auto_discover_skills)
- 7개 스킬 .md에 샘플 데이터 요구사항 섹션 추가

### 검증 완료
- DB 속성 7개 전부 생성 확인 (운동명, 종류, 시간, 칼로리, 날짜, 강도, 완료)
- 샘플 데이터 5개 삽입 확인 (아이콘 + 모든 속성값)
- 뷰 자동 생성 확인 (calendar + table + board)

---

## [0.3.0] - 2026-03-29

### Added (Phase F: Notion API 전체 기능)
- Search API (워크스페이스 검색)
- Users API (목록/조회)
- Comments API (코멘트 추가/조회)
- Page archive/restore (아카이브/복원)
- Page/DB lock (잠금/해제)
- Markdown API (마크다운 페이지 생성/조회)
- Custom Emoji API (커스텀 이모지 조회)
- DB mention, Template mention (@today, @now, @me)
- Icon helpers (emoji, external, native, custom_emoji)
- DB property: relation, formula, rollup, auto-generated types
- DB item: people, files, phone_number, relation 값 포맷
- Router: search, comment, lock, archive 엔드포인트

### Added (Phase A~E: 블록 전체 지원)
- quote (인용), table (정적 테이블), heading_4
- code block (60+ 언어), video, audio, file, pdf
- breadcrumb, equation block, synced_block
- toggle heading (is_toggleable), 4~5단 칼럼
- embed (12개 서비스: Figma, GitHub, Loom, Miro 등)
- 인라인: italic, underline, strikethrough, inline code, link, inline equation

### 전체 기능 수: 74개 (100% 구현)

---

## [0.2.0] - 2026-03-29

### Added
- **Views API 완전 구현**: 10개 뷰 타입 전부 자동 생성 (table, board, calendar, timeline, gallery, list, chart, form, map, dashboard)
- **data_source_id 자동 조회**: DB 생성 후 `data_sources[0].id` 추출 → Views API에 정확한 ID 전달
- **Tab 블록 지원**: 2026-03-25 추가된 신규 블록 타입
- **Status 속성 쓰기**: 2026-03-19 추가된 기능
- **멘션 지원**: page mention, date mention (block_builder)
- **색상 안전 처리**: `_safe_color()` 함수 — 유효하지 않은 색상 자동 폴백
- **대화 맥락 유지**: WebSocket 세션 내 conversation history + MODIFY 의도 처리
- **후속 수정**: "DB에 속성 추가해줘" → 기존 DB에 속성 추가
- **QUESTION 응답**: API 한계/기능 관련 질문에 자동 답변
- **생성 후 안내**: 전체 너비, 뷰 변경, 필터 설정 방법 안내

### Changed
- Notion API 버전 2022-06-28 → 2025-09-03 (Views API 지원)
- 모든 패턴에 뷰 자동 추가 (대시보드: 캘린더+보드, 트래커: 캘린더+갤러리, 프로젝트: 칸반+타임라인)
- DB 속성 고도화 (우선순위 select, 담당자, 5개 샘플)
- confidence 임계값 0.7 → 0.5 (불필요한 질문 감소)

### Fixed
- 색상값 검증 (`green_background` 등 Notion API 거부 방지)
- Views API `data_source_id ≠ database_id` 문제 해결

---

## [0.1.0] - 2026-03-27

### Added
- FastAPI 앱 구조 (main.py, config.py, core/, routers/, schemas/)
- AI Agent 파이프라인 (orchestrator → intent_analyzer → blueprint_generator → tools)
- Intent Analyzer: Groq / Gemini / Claude / Mock 4개 프로바이더
- Blueprint Generator: 7개 템플릿 패턴
- Tools 8개
- Notion API 클라이언트 (Mock + 실제 API, Rate Limiter, Block Builder)
- 스킬 시스템: 8개 .md 스킬 파일
- WebSocket 채팅 + REST API
- React 19 + Vite 7 + TailwindCSS 4 프론트엔드
- Unit Tests 28개 (100% 통과)
- Docker + docker-compose + Makefile + GitHub Actions CI
- 기획 문서 10개

---

# Part 2: 주차별 회고

## Week 0 (2026-03-27~29) - 기획 + 전체 구현

**완료:**
- 기획 → 개발 → Notion 실제 생성 → Views API 완전 구현
- Groq (무료) + Notion API (무료) = 비용 $0
- 28개 테스트 100% 통과
- 10개 뷰 타입 전부 동작 확인

**핵심 발견:**
- `data_source_id ≠ database_id` — Views API의 핵심 포인트
- DB 생성 후 `get_database()` → `data_sources[0].id` 추출 필수
- configuration 없이 뷰 생성하면 Notion이 자동으로 적절한 속성 매핑
- Notion API 2022-06-28에서 DB 속성 생성, 2025-09-03에서 Views API 사용
