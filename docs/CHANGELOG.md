# 변경 이력 (Changelog)

> 주요 변경사항 기록. [Keep a Changelog](https://keepachangelog.com) 형식 준수.

---

## [Unreleased]

> **Track 2 "유료급 품질" 진행 중** — 산출물을 $20-49 마켓플레이스 품질 바로 끌어올리는 작업.
> **축A(유료급 품질) 전체 완료** — A1(품질 측정), A2(셀러빌리티), A3(시각 프리미엄), A4(품질 게이트+결정성), A5(도메인 예시 검색·주입).
> **v1.0 완성 플랜 진행 중**: Phase 1(엔진 품질), 2(가치·정직), E2E 품질보정, 3(B1 대화형 수정 1차), 4(B2 캔버스 1차) 완료. 다음 Phase 5(C1 비용·성능 + C2 평가).

### Added (Phase A1 — 품질 측정 인프라)
- **유료급 품질 루브릭 (`premium_rubric`)** — 블루프린트를 0~100점 + 가격 밴드($0 / $5-15 / $20-49 / $50-99 / $100+)로 결정적 채점. 시장 리서치 기반 10개 기준(연결 DB·작동 rollup·대시보드·formula·온보딩·시각·샘플·모바일/네비, + 영상·지원은 산출물 밖으로 정규화 제외). 개선 약점 Top3 자동 도출.
- **LLM 주관 품질 심사 (`premium_judge`)** — 도메인 적합성·네이밍·레이아웃·완성도·지불의사를 LLM이 PASS/FAIL 이진 판정(self-preference bias 회피 위해 생성과 다른 모델 권장). provider 실패/예산초과 시 graceful skip. `enable_llm_judge` 설정으로 토글.
- **통합 품질 리포트 (`quality_report`)** — 구조 검증(QualityValidator) + 유료급 루브릭 + LLM 심사를 묶어 생성 결과 metadata에 부착. **A1은 비차단(측정 전용)** — 차단 게이트는 Phase A4.
- **전체 blueprint 로컬 영속성 (`history`)** — 메타데이터만 저장하던 한계를 보완해 error analysis용으로 전체 blueprint 본문을 `data/blueprints/`에 저장(DB 아님, 로컬 파일) + 보존기간 정리.

### 실데이터 검증 (Phase A1)
- golden 8 + recipe 4 baseline 측정: 멀티DB 플래그십 $50-99(최대 88점), 단순 레이아웃 대부분 $5-15 → "few-shot exemplar가 약해 AI 출력이 그 수준을 물려받음"을 정량 확인(→ Phase A2/A5 정당화).
- 라이브: 자연어→실제 AI 생성→유료급 리포트 부착 정상(독서 트래커 = $5-15), LLM judge 실제 verdict(Gemini, CRM recipe 5/5 PASS $20-49).
- 백엔드 **1,492** 테스트 통과(신규 31), ruff clean.

### Added (Phase A2 — 셀러빌리티 레이어)
- **온보딩 "시작하기" 페이지 자동 주입 (`sellability`)** — 구매자 불만 1위(빈 DB·안내 없음) 해소. 실제 DB명·뷰 반영한 템플릿 인지형 가이드(구성/사용법/맞춤설정/샘플정리). 멱등(이미 있으면 스킵).
- **상단 네비 + 목차 자동 주입** — 모바일 좌측 사이드바 스크롤 문제 해소. 하위페이지 가로 네비(column_list of link_to_page, 단일이면 link) + table_of_contents. `sub_page_ref` → 생성 후 실제 page_id 치환.
- **리스팅 키트 (`listing_kit`)** — 구조에서 결정적으로 제목·태그라인·설명·기능 불릿·≤60초 프리뷰 스크립트·추천 가격밴드 생성(판매 등록 초안). metadata 부착.

### 실데이터 검증 (Phase A2)
- golden 8 재채점: 평균 **53.6 → 60.1 (+6.5)**, flagship dashboard_widgets **88 → 92 ($100+)**. 멱등성 정상(이미 온보딩 있는 레이아웃은 네비만 적용).
- 라이브: "독서 트래커" 실제 AI 생성 → onboarding+nav+toc 적용, 유료급 점수 **44.6 → 51.2**, 리스팅 키트 생성.
- 백엔드 **1,505** 테스트 통과(A2 신규 13), ruff clean.

### Added (Phase A3 — 시각 프리미엄)
- **뷰 큐레이션 (`visual_enrich`)** — DB 속성에 맞춰 board(상태/선택별 group_by)·calendar(날짜) 자동 추가(멱등, 골든의 검증된 포맷). view_ops 클라이언트(10종 뷰)·creation_executor(date_property 이름→ID 해결)는 이미 완비 → 생성기가 안 만들던 풍부한 뷰를 채움.
- **아이콘 보강** — 메인/DB/하위페이지에 의미 있는 기본 아이콘 보장(키워드 인지: 고객→👥, 거래→💰 등). AI가 누락한 DB 아이콘을 채워 시각 완성도↑.

### 실데이터 검증 (Phase A3)
- golden 재채점: 뷰 큐레이션 작동(dashboard +3뷰, portfolio +2뷰 등). golden은 DB 아이콘 기존 보유.
- 라이브: "프로젝트 대시보드" 실제 AI 생성 → DB 아이콘 ✅ 자동 채움, table/board/calendar 다중 뷰, 리스팅에 "다중 뷰" 노출.
- 백엔드 **1,513** 테스트 통과(A3 신규 8), ruff clean.
- 참고: 뷰 풍부화는 실제 산출물·리스팅·LLM 심사엔 반영되나 결정적 루브릭 점수엔 직접 미반영(단일DB는 핵심 약점이 relation_rollup/linked_db — A5에서 해소).

### Added (Phase A4 — 품질 게이트 + 결정성)
- **품질 게이트 (`quality_report.evaluate_premium_gate`)** — 유료급 점수 + 구조 무결성으로 `premium_ready` 판정 + 미달 사유(약점 가이드 포함)를 metadata에 부착. `quality_gate_enabled` 시 orchestrator가 미달을 고지(비차단). 기준 `quality_gate_min_score`(기본 60 = $20-49).
- **blueprint pin (`history.pin_blueprint`/`load_pinned`)** — 생성 blueprint를 고정 id로 byte-stable 저장 → `execute_blueprint`(결정적)로 AI 없이 동일 재생성("이 템플릿 그대로 다시").

### Fixed (Phase A4 — 실데이터 QA에서 발견)
- **QualityValidator title/icon/color false-positive (게이트 차단급)** — 조립된 blueprint는 제목이 main_page/metadata에 있는데 top-level `title`만 확인해 **모든 조립 blueprint를 'title 없음' critical로 오판** → 게이트가 정상 프리미엄 템플릿(dashboard_widgets 92, crm 86)까지 막던 결함. title/icon/color 조회를 조립 구조까지 보도록 하위호환 수정. (A1 이전엔 `passed` 미사용으로 잠복하던 결함)

### 실데이터 검증 (Phase A4)
- 게이트 판정: dashboard_widgets(92)·crm(86)·okr(84) ✅통과, 단순 단일DB($40-57) ❌차단(사유: relation_rollup 약점). 기준대로 정확히 변별.
- 백엔드 **1,521** 테스트 통과(A4 신규 8 + 회귀 1), ruff clean.

### Added (Phase A5 — 도메인 예시 검색·주입)
- **`exemplar_retriever`** — 큐레이션된 고품질 recipe(멀티DB·relation·rollup, $50-99급)를 예시 코퍼스로 삼아, 유저 요청 도메인을 키워드/태그(+한국어 도메인 키워드)로 매칭해 생성 프롬프트에 "참고 우수 예시"로 주입. AI가 단일DB 대신 연결된 멀티DB+집계 구조를 모방하게 유도. **벡터/임베딩 RAG 아님** — 기존 golden few-shot 패턴 확장(무DB·무벡터스토어). 멀티DB 예시만 주입(단일DB·무관 요청 제외).
- `blueprint_generator`: skill_guide에 예시 힌트 배선.

### 실데이터 검증 (Phase A5)
- 검색: "고객 관리 영업 시스템"→crm, "분기 목표 성과"→okr 주입O / 독서(단일DB)·회의록(무관) 주입X. **한국어 요청 매칭 누락을 라이브에서 발견·보완**(recipe 영어 태그 → 한국어 도메인 키워드 추가).
- 라이브: "고객 관리 영업 시스템" → 실제 AI 3DB(고객/거래/활동)·relation 2개, 유료급 **70.4 ($20-49) premium_ready=True**.
- 백엔드 **1,529** 테스트 통과(A5 신규 8), ruff clean.

### Added (Phase 1 — 엔진 품질 마무리: judge→repair)
- **judge→repair 루프** — LLM 심사(A1)가 측정만 하던 것을, **FAIL 시 약점(미달 기준+약한 영역)을 피드백해 1회 재생성** 후 더 나은 결과(유료급 점수 기준) 채택. evaluator-optimizer 완성. `judge_repair_enabled` 설정 + 비용 게이트로 제한.
- 동작: judge가 "사용 가능한 단순 템플릿"엔 관대 → repair는 진짜 실패(깨짐/generic)에 발동하는 보정 장치(결정적 게이트 premium_ready와 상보).
- 라이브: 파이프라인 정상(judge PASS→재생성 없음, judge skip→graceful). 단위 5종(채택/원본유지/비활성/PASS-무repair/None).
- 백엔드 **1,534** 테스트 통과(Phase1 신규 5), ruff clean.

### Added (Phase 2 — 가치 가시화 + 정직성)
- **프론트 품질신호 표시 (`QualityPanel`)** — 백엔드 metadata로 도착하나 렌더 0이던 `premium_score/band/ready`·`listing_kit`를 라이브 프리뷰에 **판매 품질 패널**(등급 배지·판매준비·점수 바·리스팅 초안)로 표시. `BlueprintMetadata` 타입 확장.
- **가짜 데이터 제거(정직성)** — StatusBar `GPU-Cluster/Latency` 더미 텔레메트리 제거 + ProfilePage 정적 12스킬 → `/api/skills` 실데이터(실제 개수·이름) 동적 로드(실패 시 정직 고지).
- 토큰/비용 메트릭 정직화는 실제 배선이 필요해 **Phase 5(C1)에서 처리**(제거 아닌 실측).

### 검증 (Phase 2)
- 프론트 tsc+build 통과(312 모듈), eslint 0 errors(기존 a11y warn만), vitest **6 통과**(QualityPanel `bandTone` 2종 신규). 백엔드 무변경(**1,534** 유지).
- 데이터 계약 확인: 백엔드 metadata(premium_*·listing_kit) ↔ QualityPanel 소비 일치(라이브 3-tier QA에서 실측: 중간 $50-99·어려움 $100+).

### Fixed (E2E 품질 보정 — 실제 Notion E2E에서 발견)
> 검증 기준 강화: 실데이터 = **실제 Notion 생성 + rollup 집계값까지 확인**(blueprint/점수에서 멈추지 않음).
- **generic DB명 제거** — AI가 DB title 누락 시 `데이터베이스 1/2`로 폴백하던 것을, **다른 DB의 relation이 가리키면 그 이름으로 유추**(고객의 '거래' relation→DB1 ⇒ '거래').
- **status 옵션 coercion** — AI가 옵션을 문자열(`"시작 전"`)로 주면 Notion 400(`options should be an object`)→status 드롭하던 것을 select과 동일하게 `{name,color}` 객체로 강제.
- **live_qa 하네스 강화** — rollup **집계값**까지 검증 + generic DB명 플래그(구조·샘플행 수만 보던 한계 보정).

### 검증 (E2E 품질 보정)
- **실제 Notion E2E 재확인**: AI "고객 관리 CRM" → DB명 **고객/거래(정상)**, rollup '총 거래액' **실집계 [₩2.5M,2M,3M,9M]**. recipe crm → '총 딜금액' [₩3M,80M,5M,15M,50M].
- 백엔드 **1,540** 테스트(신규 6), ruff clean.

### Added (Phase 3 — B1 AI 대화형 수정, 1차)
- **LLM 수정 분류기 (`modify_classifier`)** — ModifyHandler의 regex 분류(자유 발화·미지원 op 누락) 대신 LLM이 요청+템플릿 맥락으로 operation 분류. provider 실패 시 **regex 폴백**(robustness 유지).
- **recolor 핸들러** — "색 바꿔줘/파란색으로" → **라이브 Notion 페이지 블록 색을 실제 변경**(callout/heading/quote/toggle). regex엔 핸들러조차 없던 기능.
- `handle_modify`: LLM 분류 우선 → 기존 검증된 핸들러 재사용 + recolor 신설.

### Fixed (Phase 3 — 실 Notion E2E에서 발견)
- **recolor가 rich_text 누락으로 Notion 400**('rich_text should be defined') → heading/quote/toggle 실제 변경 실패+성공 오보고하던 것을, 기존 rich_text/icon 보존 + 실패(fallback)는 카운트 제외로 수정.

### 검증 (Phase 3)
- 백엔드 **1,547** 테스트(B1 신규 7), ruff clean. **실 Notion E2E: 생성→"보라색으로 바꿔줘"→callout/heading/quote/toggle 4/4 실제 purple 변경 확인.**
- 후속(B1 확장): op별 LLM 파라미터 추출(현재 분류만 LLM·파라미터는 핸들러 자체 파싱), 구조화 diff/스코프드 편집.

### Added (Phase 4 — B2 캔버스 UX, 1차)
- **버전 히스토리/롤백 (`VersionRail` + `lib/revisions`)** — 세션 내 도착한 blueprint 리비전을 프리뷰 상단에 버전 칩(v1·v2·…·최신)으로 표시, 클릭해 이전 버전 열람. (2-pane 라이브 프리뷰는 기존)
- 검증: 프론트 tsc+build·eslint 0 errors·vitest **9**(`extractRevisions` 3 신규). 프론트 전용(Notion 미접촉)이라 build+단위로 검증.
- 후속(B2 확장): 스코프드 편집(섹션 선택→수정)·생성 중 점진 채워짐.

---

## [0.1.7] - 2026-06-01

> 제품이 UI·AI 파이프라인 전 경로에서 실제로 end-to-end 작동하게 된 안정화 릴리스.
> 백엔드 **1,461** 테스트 + 프론트 Vitest/Playwright E2E 통과 + 실제 Notion 라이브 검증.
> (production-stable 1.0 선언은 더 넓은 스킬/베타 검증 후로 보류.)

### Fixed (2026-06-01 — 라이브/UI 검증에서 발견한 릴리스 차단급 결함)
- **AI 파이프라인 relation 링크/rollup 집계 복구 (CRITICAL)** — AI가 sample relation 값을 제목 문자열·`{db_index,item_index}`·`{title,id}`·리스트 등 다양하게 내보내는데 제목 문자열만 처리해 매칭 실패 → relation 0건 → rollup 0/None이었다. 다포맷 해석 + single_property 양방향 **미러링**으로 어느 쪽 rollup이든 집계되도록 복구. (그동안 recipe 경로만 검증돼 가려져 있었음)
- **WS 미연결 시 무생성 함정 제거** — WebSocket 미연결 시 `/preview`(미리보기 전용, Notion 미생성)로 폴백하며 "성공"처럼 보이던 문제 → 미연결 경고 배너 + 정직한 안내 + 자동 재연결. 실제 UI 승인→생성 E2E 추가.
- **차트 뷰 x_axis/y_axis dict 크래시** — dict를 멤버십 검사해 TypeError로 차트 포함 템플릿(가계부 등) 생성 전체가 실패하던 문제 수정.
- **Groq/OpenAI json 모드 400** — `response_format=json_object`는 메시지에 'json' 단어 필수. user 메시지에 보장 → Gemini 쿼터 소진 시 Groq가 신뢰할 폴백이 됨.
- **AI 무title 시 영어 기본값** — 'My Template'이 노션 제목이 되던 문제 → 사용자 요청에서 한국어 제목 생성. 날짜 `{start,end}` dict 미처리, 제목 선두 이모지 중복(`📚 📚`)도 수정.
- **provider 폴백 신뢰성 (CRITICAL)** — copilot이 `databases` 없는 빈 dict를 반환하면 '성공'으로 처리돼 groq/gemini 폴백을 건너뛰던 결함. 유효(databases 존재) 응답만 성공으로 보고, 무효면 다음 provider로 캐스케이드(copilot→groq→gemini→claude). `_fallback_candidates`를 circuit-aware(429 차단 provider 건너뜀)·groq 우선·copilot 포함으로 개선.
- **AI 무title 시 긴 메시지가 제목 / DB명 'Items' 중복** — 제목은 첫 구 30자 캡, DB명은 고유 한국어('데이터베이스 N').
- **CRM recipe '남은일수' formula 미계산** — 딜 샘플에 '예상 마감일' 날짜가 없어 formula가 전부 None이던 문제 → 미래 날짜 보완(라이브: [91,13,64,38,23]일).
- **AI가 properties를 list로 반환 시 크래시 (CRITICAL)** — Groq가 properties를 dict 대신 list로 내보내면 `validate_ai_content`의 `props.values()`가 `'list' object has no attribute 'values'`로 크래시 → Gen-Eval 3회 전부 실패 → smart_fallback. list 3형태를 dict로 정규화. 라이브: '독서 모임'이 일관 smart_fallback → 이제 ai_dynamic(참석 횟수 rollup [3,2,2,3,3] 집계).

### Added (2026-06-01)
- **전 provider 실패 시 generic 폴백 사용 고지** — 모든 AI provider가 실패(한도/빈응답)해 smart_fallback이 쓰이면 system 경고를 emit('기본 템플릿 사용, 재시도 시 맞춤 설계')해 silently 잘못된 템플릿이 나오던 혼란 방지.
- **실제 UI 승인→Notion 생성 E2E** (`frontend/e2e/approval.spec.ts`) — Approval Gate가 confirm 없이 멈추지 않고 실제 생성까지 도달함을 보증.

### Changed (2026-06-01)
- **양방향 relation = single_property + 샘플 링크 미러링** (이전 dual_property 방식 폐기) — dual_property가 반대편 relation 이름을 Notion 자동명으로 덮어써 그 측 rollup을 영구 미집계로 깨뜨렸음(CE-01). 전부 single_property로 생성해 선언 이름을 보존하고, 후처리에서 양방향을 명시 충전.
- **미사용 중복 채팅 UI 제거** — App은 DashboardPage→ChatPanel 사용. 임포트되지 않던 MainLayout→ChatWindow 체인(5파일) 삭제.

### Known limitations (0.2.0 시점 — 정직 고지)
- AI 생성은 provider 가용성에 의존. Gemini 키 쿼터 소진(429) 시 copilot/Groq에 의존하며, 둘 다 일시 실패하면 generic 폴백 템플릿으로 떨어질 수 있음.
- AI 샘플 데이터의 날짜가 과거로 생성될 수 있어 D-Day/경과일 수식이 음수/큰 값이 될 수 있음(로직은 정상).
- 단일 워커 권장(외부 상태 저장소 미사용). 48개 스킬 중 일부는 라이브 미검증.

### Added (이전 하드닝 누적)
- **세션 LLM 호출 예산** (`app/core/cost_control.py`) — ContextVar 기반 동시세션 격리, 호출 상한(기본 40)으로 비용 폭주 방지
- **라이브 QA 하네스** (`backend/scripts/live_qa.py`) — 실제 Notion 생성 후 페이지/DB/샘플행/속성 정량 검증 (recipe·prompt 모드)
- 보안: `.gitleaks.toml` + `.pre-commit-config.yaml`(gitleaks/detect-private-key/ruff) + CI 전체 히스토리 시크릿 스캔
- CSP 보안 헤더, WebSocket IP 연결 rate limit, CORS `*`+credentials 자동 차단
- 핵심 스킬(finance/project/crm)에 필수 계산속성(rollup/formula) 가이드 명문화
- 레시피/골든 품질 회귀 게이트 테스트, ADR 0001(안정성 횡단 결정)

### Changed
- **Provider Fallback 실배선** — Gen-Eval/pipeline/agent_loop가 `resolve_with_fallback` 사용, copilot 폴백 포함
- **AI 생성 실패 시 작동하는 provider로 자동 폴백** — 1차 None 반환 시 키 있는 provider로 전환해 실제 AI 생성 보장
- **Approval Gate 실배선** — 미리보기 후 승인 대기(타임아웃 시 중단), REST/Task는 자동 승인
- AgentLoop 스텝 하드캡(MAX_STEPS=15), Notion SDK 버전 핀
- 서브페이지 `name`/`title` 키 호환(`_subpage_title`) — 서브페이지 콘텐츠 누락 수정
- 제목 정리 — 색상 지시 제거(토큰 완전일치, '블루베리'·'그린팀' 보존)

### Fixed
- `import_blueprint` 항상 500 → execute_blueprint 래퍼 + Pydantic 검증
- `_current_result` AttributeError, agent_loop `loop_result` UnboundLocalError
- 단일 DB formula 후처리 누락, `BudgetExceededError` 광역 except에 삼켜지던 문제
- 테스트 격리 — conftest가 LLM/Notion 키·circuit breaker·WS상태 미리셋

### Quality
- 약 40개 결함 발견·수정 (라이브 E2E + UI E2E + 멀티에이전트 자기검증), 전부 회귀테스트화
- 백엔드 테스트 1,374 → **1,446**, 프론트 Vitest + Playwright E2E(스모크 + 승인→생성) 신규

### Gate 3~6 (추가 하드닝)
- **Gate 3 API**: query 페이지네이션(has_more), rate limiter jitter + Retry-After, data_source 마이그레이션 정합
- **Gate 4 테스트/관측성**: CI에 통합테스트 포함, `/api/metrics/summary` p50/p95+토큰, Prometheus `/metrics`, 프론트 Vitest, Playwright E2E(스모크)
- **Gate 5 릴리스**: 버전 SSOT(`app.__version__`)+버전 일치 CI, setup.sh env키 수정, pip-licenses 라이선스 CI, release SBOM(syft)
- **Gate 6 공개**: GOVERNANCE/MAINTAINERS/SUPPORT/CODEOWNERS, README·SECURITY 정직화(단일워커·결정성·재판매권리), 예제 갤러리, a11y 린트(jsx-a11y warn)

---

## [0.1.6] - 2026-05-18

### Changed
- 영문 README.md 신규 작성 — 기존 한국어 README는 README.ko.md로 분리
- 전체 버전 통합 — frontend(8.1.0), backend(0.1.4), 문서(v8.x) → v0.1.6으로 일원화
- 문서 전면 최신화 — ARCHITECTURE, API, DEPLOYMENT, TEST_GUIDE, SKILL_GUIDE, BLOCK_SUPPORT, CURRENT_STATUS, AGENT_DESIGN, ROADMAP, SECURITY
- 테스트 수 1,359 → 1,374개 반영, 라우터 수 7 → 8개 반영
- `.env.example`에 누락 변수 5개 추가 (RATE_LIMIT_RPM, CORS_ORIGINS, INPUT_MIN/MAX_LENGTH, APPROVAL_TIMEOUT_SECONDS, GEN_EVAL_MAX_RETRIES)

---

## [0.1.4] - 2026-05-18

### Security
- OAuth 토큰 전달 방식 변경 — URL fragment 노출 제거, 일회용 교환 코드 방식으로 전환
- SecurityHeadersMiddleware 추가 (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Referrer-Policy)
- `.gitignore` 보강 — `*.pem`, `*.key`, `*.p12`, `credentials.json`, `service-account*.json` 추가
- `_pending_states` DoS 방어 — 최대 1,000개 제한 추가
- SSE 스트리밍 에러에 `sanitize_error()` 적용 — 내부 정보 노출 방지
- README에 "로컬 전용 서버" 보안 경고 추가

---

## [0.1.3] - 2026-05-18

### Fixed
- Docker 이미지 태그 소문자 변환 — GHCR push 시 `repository name must be lowercase` 에러 수정
- README 배너를 커스텀 PNG 이미지로 교체

---

## [0.1.2] - 2026-05-18

### Fixed
- FOUC(Flash of Unstyled Content) 수정 — 새로고침 시 Material Symbols 아이콘 텍스트 노출 방지
  - `index.html`에 critical CSS 인라인 (`#root { opacity: 0 }`)
  - Material Symbols `font-display: block` 적용
  - `document.fonts.ready` 기반 앱 reveal (최대 3초 타임아웃)
- ruff 린트 오류 2건 수정 (N806, F541)
- ruff format 3개 파일 포매팅 적용

### Changed
- 레포명 `notion_ai_agent` → `Notion_Forge` 전체 반영 (17개 파일)
- 문서 최신화: ARCHITECTURE, AGENT_DESIGN, CURRENT_STATUS, CHANGELOG, DEPLOYMENT, README, CLAUDE.md
- 듀얼 API 전략 문서화 (쓰기: 2022-06-28 / 읽기·뷰: 2026-03-11)
- PostProcessor 13종 자동 수정 반영 (QualityValidator 3계층 → Gen-Eval + PostProcessor)

### Added
- widget_builder 테스트 12개
- workers ops (Workers + External Agents API) 테스트 38개
- 테스트 총 1,359개 (커버리지 80.30%)

---

## [0.1.0] - 2026-05-18 (첫 오픈소스 공개 릴리스)

### Added (Notion API 듀얼 버전 + Workers 통합)

**Phase 1: API 최신화 + 듀얼 버전 전략**
- Notion API 듀얼 버전: 쓰기(2022-06-28) + 읽기/뷰/Workers(2026-03-11)
- 2026-03-11이 DB 생성 시 속성을 무시하는 문제 발견 → legacy 클라이언트 병행으로 해결
- Comments API: 생성/조회/수정/삭제 + 스레드 댓글
- File Upload API: 서버→Notion 직접 파일 업로드
- Data Sources API: 외부 데이터소스 연동 인프라

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
- 테스트 1,320개 (1,215 → 1,320, +105)

**Phase 5: 안정화 — DB 속성/샘플 데이터 정상화**
- `_http_client_legacy` (2022-06-28) 추가: DB/페이지 생성 시 속성 정상 처리
- 한국어 동의어 매핑 30+ 패턴: 블루프린트 키 → 실제 DB 속성 자동 매칭
- QualityValidator 파이프라인 분리: 불필요한 재생성 방지
- PostProcessor 13종 자동 수정으로 블루프린트 품질 보장
- DB 생성 시 속성 개별 추가 폴백: validation 에러 시 title만 생성 → PATCH로 속성 추가

### Changed
- README 전면 개편: Hermes Agent 수준 오픈소스 문서 구조
- CONTRIBUTING.md: 확장 가이드 (프로바이더/도구/스킬/뷰) 추가
- SECURITY.md: GitHub URL 업데이트
- GitHub 리포지토리 URL: `JaylenAI/Notion_Forge`로 통일
- 머지 완료된 feature 브랜치 26개 정리 (→ main + dev만 유지)

---

# Pre-release 개발 이력

> 아래는 오픈소스 공개 전 내부 개발 과정의 기록입니다.

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
