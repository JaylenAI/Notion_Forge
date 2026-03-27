# 변경 이력 + 회고 (Changelog & Retrospective)

> 주요 변경사항 + 주차별 회고 (가짜연구소 발표용)

---

# Part 1: 변경 이력

## [0.1.0] - 2026-03-27

### Added (Backend)
- FastAPI 앱 구조 (main.py, config.py, core/, routers/, schemas/)
- AI Agent 파이프라인 (orchestrator → intent_analyzer → blueprint_generator → tools)
- Intent Analyzer: Groq (gpt-oss-120b) / Gemini / Claude / Mock 4개 프로바이더
- Blueprint Generator: 7개 템플릿 패턴 (dashboard, tracker, bookmark, project, note, onboarding, crm)
- Tools 8개: create_page, create_database, add_blocks, add_database_items, create_columns, apply_color_theme, link_databases, generate_cover
- Notion API 클라이언트 (Mock + 실제 API, Rate Limiter, Block Builder)
- 스킬 시스템: 8개 .md 스킬 파일 (영어, 공식 플러그인 패턴 참고)
- WebSocket 채팅 라우터 (/ws/chat)
- REST API (generate, preview, patterns)
- Unit Tests 28개 (100% 통과)
- 실제 Notion 페이지 생성 성공 확인

### Added (Frontend)
- React 19 + Vite 7 + TailwindCSS 4 + Zustand 5
- 다크 테마 UI (사이드바 + 채팅 + 설정)
- ChatWindow: 빈 상태 템플릿 카드, 메시지 타입별 스타일링
- SettingsPanel: Notion API 키 + Page ID 입력, 연결 테스트
- ProgressBar: 4단계 실시간 진행률
- WebSocket + REST API 폴백 지원
- localStorage 설정 저장

### Added (Infra)
- Docker + docker-compose (dev/prod 분리, multi-stage Dockerfile)
- Makefile (dev, test, lint, build, clean)
- GitHub Actions CI
- .env.example + .gitignore

### Added (Docs)
- 기획 문서 10개 (PLANNING, ARCHITECTURE, AGENT_DESIGN, USER_SCENARIOS, API, SETUP, DEVELOPMENT_PLAN, TEST_GUIDE, ONBOARDING, CHANGELOG)
- 스킬 파일 참고 자료 (content-writing/reference/)

---

# Part 2: 주차별 회고

## Week 0 (2026-03-27) - 기획 + 전체 구현

**목표:**
- [x] 프로젝트 주제 확정
- [x] 기획서 + 시장조사 작성
- [x] 전체 개발 구조 구축
- [x] AI Agent 파이프라인 완성
- [x] Notion API 실제 생성 테스트
- [x] 프론트엔드 UI 구현

**완료:**
- 노션 템플릿 자동화 AI Agent 주제 확정 → 기획 → 개발 → 실제 생성까지 1세션 완료
- Groq (무료) + Notion API (무료) 조합으로 비용 $0 달성
- 28개 테스트 100% 통과
- 실제 Notion 워크스페이스에 대시보드 생성 성공

**배운 것:**
- Notion API v3에서 parent에 `type` 필드 필수
- DB 속성 이름이 API 생성 후 변경될 수 있음 (title → Name 등)
- 칼럼(column) 안에 칼럼(column_list) 중첩 불가
- Groq gpt-oss-120b가 의도 분석에 충분히 좋음 (Gemini보다 안정적)

**다음:**
- 프론트엔드 UI 디자인 레퍼런스 적용
- 샘플 데이터 품질 개선
- 웹 배포 (Vercel + Railway)
