# 변경 이력 + 회고 (Changelog & Retrospective)

> 주요 변경사항 + 주차별 회고 (가짜연구소 발표용)

---

# Part 1: 변경 이력

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
