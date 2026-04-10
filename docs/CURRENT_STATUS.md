# 진행 현황 (Current Status)

> 최종 업데이트: 2026-04-10
> 현재 브랜치: dev-2
> 버전: v6.1.0

---

## 전체 진행률

```
Notion API 74개 기능       [██████████] 100%
AI 자유 설계 시스템         [██████████] 100%
AI 프로 디자인 시스템       [██████████] 100%
스킬 시스템 12개           [██████████] 100%
프론트엔드 UI 5페이지      [██████████] 100%
NotionRenderer 14블록     [██████████] 100%
Library 수동 저장          [██████████] 100%
테스트 39/39              [██████████] 100%
프론트엔드 UI/UX 고도화    [██████████] 100%
페이지 전체 너비           [██████████] 100%
링크드 DB 뷰              [██████████] 100%
블록 position 제어        [██████████] 100%
미리보기=실제 일치         [██████████] 100%
DB 고도화 (desc/icon)     [██████████] 100%
뷰 고도화 (group_by등)    [██████████] 100%
코멘트 강화               [██████████] 100%
페이지 이동/마크다운       [██████████] 100%
복잡도 스케일링           [██████████] 100%
링크드 DB뷰+필터          [██████████] 100%
── v6.0.0 신규 ──
Relation/Rollup/Formula   [██████████] 100%
서브페이지 AI 패스스루     [██████████] 100%
혼합 리치텍스트            [██████████] 100%
디자인 토큰 시스템         [██████████] 100%
멀티턴 대화형 수정         [██████████] 100%
복잡도/언어 선택 UI        [██████████] 100%
Blueprint Export/Import   [██████████] 100%
커뮤니티 레시피 갤러리     [██████████] 100%
다국어 지원 (한/영/일)     [██████████] 100%
멀티 에이전트 파이프라인   [██████████] 100%
Document-to-Notion        [██████████] 100%
OAuth 연동                [██████████] 100%
배포 준비                 [██████████] 100%
```

---

## 완료 기능

### AI Agent
- ✅ AI 자유 설계 (blocks[] + databases[] 모두 AI가 결정)
- ✅ 12개 스킬 (track/collect/manage/plan/organize/guide/hub/finance/journal/content/learn/crm)
- ✅ 4개 AI 프로바이더 (Gemini/Groq/Claude/OpenAI)
- ✅ 동적 모델 선택 (API로 모델 목록 조회)
- ✅ 스마트 폴백 6개 (AI 실패 시 키워드 기반)
- ✅ 실시간 스트리밍 (매 단계 WebSocket + 실시간 progress 로그)

### AI 프로 디자인 시스템 (v5.1.0+)
- ✅ 시스템 프롬프트 전면 재작성 (Thomas Frank/Easlo 수준 디자인 규칙 50+개)
- ✅ 색상 팔레트 2-3색 제한 규칙 (스킬별 추천 팔레트 7종)
- ✅ 대시보드 컬럼 레이아웃 30/70 분할
- ✅ 정보 계층 구조 강제 (callout→spacing→columns→DB→toggle)
- ✅ 아마추어 안티패턴 11가지 방지 규칙
- ✅ DB 뷰-속성 자동 매칭 규칙 (status→board, date→calendar 등)
- ✅ 커버 이미지 20개 (색상 10 + 카테고리 10)
- ✅ 12개 스킬 전체에 Pro Design Guide 섹션
- ✅ 블록 다양성 강제 (quote/to_do/numbered_list 최소 3개)
- ✅ 서브페이지 내용 자동 생성 (빈 페이지 방지)
- ✅ **미리보기=실제 노션 일치** (column 안 database_ref 금지 규칙)

### Notion API (74개 + 확장)
- ✅ 블록 30+ 종, 인라인 서식 전체, 미디어 전체
- ✅ DB 뷰 10종 (Views API + data_source_id)
- ✅ 샘플 데이터 자동 삽입 (5개+, status 한→영 매핑 50+패턴)
- ✅ TYPE_ALIASES 17개, Legacy API 호환
- ✅ 컬럼 width_ratio 지원 (30/70 대시보드 분할)
- ✅ 페이지 전체 너비 자동 설정 (Internal API, token_v2)
- ✅ 링크드 DB 뷰 생성 (Views API create_database)
- ✅ **블록 position 제어** (after_block, page_end)
- ✅ **서브페이지 하단 배치** (position: page_end)
- ✅ DB title 속성 자동 보장
- ✅ 이모지 유효성 자동 폴백
- ✅ **DB description/icon/cover** 지원
- ✅ **뷰 group_by/sub_group_by/quick_filters/properties/position** 지원
- ✅ **블록 레벨 코멘트 + 답글 스레드** (discussion_id)
- ✅ **페이지 이동 API** (move_page — 부모 변경)
- ✅ **마크다운 콘텐츠 교체** (update_page_content_markdown)
- ✅ **링크드 DB뷰 + 필터** (같은 DB를 다른 필터로 다른 위치에 표시)
- ✅ **복잡도 스케일링** (simple 10-15 / medium 15-25 / complex 25-40 블록)
- ✅ **3컬럼 대시보드 레이아웃** (위젯 그리드 + toggle 네비게이션)

### 프론트엔드 (기본)
- ✅ 다크 테마 5페이지 (Dashboard/Library/Integrations/Profile/Support)
- ✅ 프롬프트 스타터 카드 6개 (원클릭 생성)
- ✅ NotionRenderer: 14개 블록 + 4개 DB 뷰 (Table/Board/Calendar/Gallery)
- ✅ Library 수동 저장 (Save to Library 버튼, 중복 방지)
- ✅ 완료 후 액션 버튼 (Open in Notion + Save to Library + Copy URL + Create Another)
- ✅ 에러 상태 UI + ErrorBoundary 복구 버튼
- ✅ UI 영어 통일
- ✅ Mock 데이터 완전 제거 → 실제 데이터 연동

### 프론트엔드 UI/UX 고도화 (v5.0.0+)
- ✅ 채팅 메시지 마크다운 렌더링 (react-markdown + remark-gfm)
- ✅ 메시지 타임스탬프 표시 (hover 시 "3분 전" 상대시간)
- ✅ 채팅 히스토리 세션 관리 (자동저장/복원, 최대 50개)
- ✅ 다크/라이트 모드 토글 (CSS 변수 기반 테마 시스템)
- ✅ 모바일 반응형 (768px 이하 탭 전환, 오버레이 사이드바)
- ✅ 키보드 단축키 (⌘N 새 템플릿, ⌘K 커맨드 팔레트)
- ✅ 생성 중 취소 버튼 (AbortController + WebSocket cancel)
- ✅ 토스트 알림 (react-hot-toast — 저장/연결/에러 피드백)
- ✅ 미리보기 줌 인/아웃 (50%~150%, 5단계)
- ✅ Notion URL 복사 버튼 (클립보드 + 토스트 확인)
- ✅ 프롬프트 템플릿 라이브러리 (4개 카테고리 × 18개 프롬프트)
- ✅ 커스텀 리사이저블 패널 (라이브러리 의존 제거, 순수 구현)
- ✅ 실시간 progress 로그 스트림 (생성 과정 실시간 표시)
- ✅ PRO PLAN 제거, Support를 nav 항목으로 이동
- ✅ 한글 IME 입력 수정 (isComposing 체크)

### 테스트
- ✅ 39/39 통과 (28 unit + 10 integration + 1)
- ✅ 실제 Notion 생성 QA 8건 전부 성공
- ✅ E2E 테스트 L1~L3 전부 성공 (샘플 15/15)

### v6.0.0 신규 기능 (2026-04-08)

#### Phase A: 템플릿 품질 프로화
- ✅ Relation + Rollup + Formula 자동 생성 (DB 간 연결, 수식, 집계)
- ✅ 서브페이지 AI 블록 패스스루 (하드코딩 덮어쓰기 버그 수정)
- ✅ 혼합 리치텍스트 포맷팅 (bold+color, rich_text 배열 지원)
- ✅ 디자인 토큰 시스템 (카테고리별 이모지/색상/스타일 통일)

#### Phase B: 멀티턴 대화형 수정
- ✅ 속성 추가/삭제/변경 (select, date, number, text, checkbox 등)
- ✅ 뷰 추가/변경 (board, calendar, gallery, timeline, table, list)
- ✅ DB 추가 (AI 기반 새 DB 자동 설계 + 생성)
- ✅ Relation 연결 ("프로젝트랑 태스크 연결해줘")
- ✅ Formula 추가 (D-Day, 진행률, 총액, 상태 이모지 등)
- ✅ 서브페이지 추가 ("새 하위 페이지 추가해줘")
- ✅ 블록 추가 (FAQ, 섹션, 텍스트)

#### Phase C: 사용자 경험 + 레시피
- ✅ 복잡도 선택 UI (Simple/Standard/Advanced) + 백엔드 연동
- ✅ 다국어 선택 UI (KR/EN/JP) + AI 응답 언어 매칭
- ✅ Blueprint JSON Export/Import (LivePreview 툴바)
- ✅ 커뮤니티 레시피 갤러리 (recipes/ + API + 프론트엔드 UI)
- ✅ i18n 시스템 (한/영/일 번역 키)

#### Phase D: AI 고도화 + 배포 준비
- ✅ 멀티 에이전트 파이프라인 (Architect→Designer→Content→Validator)
- ✅ Document-to-Notion (CSV/MD/TXT/PDF → 자동 템플릿 생성)
- ✅ OAuth 연동 (Notion OAuth 플로우 — 토큰 복붙 제거)
- ✅ 배포 준비 (.env.example 정리, Docker 최적화, 버전 6.0.0)

#### 커스텀 스킬 시스템 (v6.0.0)
- ✅ 커스텀 스킬 CRUD API (/api/skills — 생성/조회/수정/삭제)
- ✅ custom_skills/ 디렉토리 자동 로딩 (내장 12개 + 유저 커스텀)
- ✅ 커스텀 스킬 우선 로딩 (같은 이름이면 커스텀 우선)
- ✅ Integrations 페이지에 Custom Skills 관리 UI
- ✅ AI 프롬프트에 커스텀 스킬 자동 주입

---

## v6.1.0 변경사항 (2026-04-10 — API 파이프라인 완성 + 프롬프트 전환)

### Views API configuration 파이프라인 완성
- ✅ `create_view()`에 `configuration` 파라미터 추가 — AI blueprint의 뷰 설정이 실제로 반영됨
- ✅ `_build_view_configuration()` 메서드 — 10개 뷰 타입 전체 config 빌드 (board cover, gallery card, chart x/y축, timeline arrows 등)
- ✅ `create_linked_view()`에도 `group_by`, `configuration` 파라미터 추가
- ✅ modify 흐름에서도 board/gallery 뷰 추가 시 cover 자동 설정
- ✅ configuration 에러 시 자동 폴백 (config 제거 후 재시도)

### 블록/뷰/페이지 CRUD API 완전 구현
- ✅ `update_view()` — 뷰 설정 수정
- ✅ `delete_view()` — 뷰 삭제
- ✅ `list_views()` — DB 뷰 목록 조회
- ✅ `get_view()` — 뷰 상세 조회
- ✅ `get_block()`, `get_block_children()` — 블록 조회 (페이지네이션 자동)
- ✅ `update_block()` — 블록 내용 수정
- ✅ `delete_block()` — 블록 삭제
- ✅ `query_database()` — DB 항목 필터/정렬 쿼리
- ✅ `get_page()`, `update_page()`, `delete_page()` — 페이지 CRUD

### 멀티턴 수정 기능 확장
- ✅ 뷰 삭제 ("캘린더 뷰 삭제해줘") — list_views → delete_view 활용
- ✅ 블록 삭제 ("'FAQ' 블록 삭제해줘") — get_block_children → delete_block 활용

### 프롬프트 "규칙" → "메뉴판" 전환
- ✅ 하드코딩 강제 규칙 제거 ("ALWAYS include", "MUST have 3 views" 등)
- ✅ View Catalog 섹션 추가 — 10개 뷰 타입별 configuration 예시 + 사용 가이드라인
- ✅ 핵심 철학 전환: "Match the user's intent — no more, no less"
- ✅ tab 블록 프롬프트에 사용법 추가

### 기존 테스트 버그 수정
- ✅ `test_build_database_properties_select` — title 속성 누락 문제 수정

---

## 개발 예정 (v7.0.0 — 템플릿 품질 혁신)

### 우선순위 최상 — 스마트 폴백 고도화 (F-1~F-6)

| # | 항목 | 상태 | 설명 |
|---|------|------|------|
| F-1 | 폴백 12개 (스킬별) | ❌ 미개발 | 현재 6개→12개, 프로 레이아웃 |
| F-2 | 폴백에 column_list | ❌ 미개발 | 모든 폴백에 3칼럼 stat cards |
| F-3 | 폴백에 formula 포함 | ❌ 미개발 | D-Day, 진행률 등 |
| F-4 | 폴백에 뷰 4-5개 | ❌ 미개발 | table+board+calendar+chart |
| F-5 | 폴백에 sub_pages+blocks | ❌ 미개발 | 3개 서브페이지 + 실제 콘텐츠 |
| F-6 | 폴백에 quote/to_do/table | ❌ 미개발 | 다양한 블록 믹스 |

### 우선순위 상 — 후처리 자동화 (C-1~C-5)

| # | 항목 | 상태 | 설명 |
|---|------|------|------|
| C-1 | 뷰 자동 보강 | ❌ 미개발 | AI가 뷰 빼먹으면 속성 기반 자동 추가 |
| C-2 | Formula 자동 추가 | ❌ 미개발 | date→D-Day, status→진행률 자동 |
| C-3 | DB description/icon 자동 | ❌ 미개발 | 비어있으면 자동 생성 |
| C-4 | group_by 자동 설정 | ❌ 미개발 | board→status/select 자동 |
| C-5 | Quick filter 자동 | ❌ 미개발 | board/table에 status filter 자동 |

### 우선순위 중 — Copilot SDK 연동 (S-1~S-4)

| # | 항목 | 상태 | 설명 |
|---|------|------|------|
| S-1 | OpenAI 호환 엔드포인트 | ❌ 미개발 | Copilot SDK → OpenAI 포맷 요청 |
| S-2 | config에 copilot_api_key | ❌ 미개발 | .env에 COPILOT_API_KEY 추가 |
| S-3 | max_tokens 8192 | ❌ 미개발 | GPT-4o용 토큰 증가 |
| S-4 | 프로바이더 우선순위 | ❌ 미개발 | Copilot > Claude > Gemini > Groq |

### 기타

| 항목 | 상태 | 설명 |
|------|------|------|
| 드래그 앤 드롭 블루프린트 재배치 | ❌ 미개발 | LivePreview에서 카드 드래그 순서 변경 |
| 즐겨찾기 퀵 액세스 | ❌ 미개발 | 사이드바에 starred 템플릿 바로가기 |
| 실시간 연결 품질 모니터 | ❌ 미개발 | WebSocket ping/pong latency |
| 배포 (Vercel + Railway) | 대기 | 프로덕션 배포 |
| 시연 영상 + 발표 | 대기 | 사용자 직접 준비 |
