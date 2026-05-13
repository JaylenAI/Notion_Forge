# 개발 계획 + 로드맵 (Development Plan & Roadmap)

> 모듈별 기능 목록 + 주차별 로드맵 + 진행 현황
> 최종 업데이트: 2026-03-27

---

## 1. 전체 일정: 8주 (2026년 4월 ~ 5월)

```
Week 1  ──── [Phase 0] 환경 세팅 + PoC ──── "페이지 1개 자동 생성 성공"
Week 2~3 ─── [Phase 1] MVP ──────────────── "채팅으로 5개 템플릿 생성"
Week 4~5 ─── [Phase 2] 고도화 ───────────── "다중 페이지 + 디자인 테마"
Week 6~7 ─── [Phase 3] 완성 & 배포 ──────── "프로덕션 배포 완료"
Week 8  ──── [Phase 4] 발표 & 오픈소스 ──── "가짜연구소 발표 + 공개"
```

---

## 2. 모듈 구성

```
NotionForge
├── [BE] Core          # FastAPI 앱, 설정, 미들웨어
├── [BE] Agent         # AI Agent (의도 분석, 구조 설계, 오케스트레이션)
├── [BE] Tools         # Agent가 사용하는 도구 (8개)
├── [BE] Notion        # Notion API 클라이언트, 유틸
├── [BE] Patterns      # 템플릿 패턴 라이브러리
├── [BE] Routers       # API 엔드포인트
├── [FE] Chat UI       # 채팅 인터페이스
├── [FE] Components    # UI 컴포넌트
├── [TEST] Tests       # 단위/통합/E2E 테스트
└── [INFRA] Deploy     # 배포, CI/CD
```

---

## 3. Phase별 상세

### Phase 0: 환경 세팅 & 검증 (Week 1) — 8개 기능

**목표**: 기술 스택 검증 + 개발 환경 완성

| # | 기능 | 모듈 | 상태 |
|---|------|------|------|
| 1 | FastAPI 앱 초기화 (main.py, CORS, 미들웨어) | Core | ❌ |
| 2 | 환경변수 관리 (config.py, .env) | Core | ❌ |
| 3 | 에러 핸들링 (전역 핸들러, 커스텀 예외) | Core | ❌ |
| 17 | Notion API 클라이언트 래퍼 | Notion | ❌ |
| 18 | Rate Limiter (3req/s + 지수 백오프) | Notion | ❌ |
| 19 | Block Builder 유틸 | Notion | ❌ |
| 28 | React + Vite 프로젝트 초기화 | Frontend | ❌ |
| 39 | Notion MCP 서버 설정 | Infra | ❌ |

**산출물**: 개발 환경 완성 + PoC (1개 템플릿 자동 생성)

---

### Phase 1: MVP (Week 2~3) — 13개 기능

**목표**: 채팅 → AI 분석 → 단일 페이지 템플릿 생성

| # | 기능 | 모듈 | 상태 |
|---|------|------|------|
| 5 | Intent Analyzer (Claude API 의도 분석) | Agent | ❌ |
| 6 | Blueprint Generator (의도 → JSON 구조) | Agent | ❌ |
| 7 | Agent Orchestrator (Tool 선택/실행/순서) | Agent | ❌ |
| 9 | Tool: create_page | Tools | ❌ |
| 10 | Tool: create_database | Tools | ❌ |
| 11 | Tool: add_blocks | Tools | ❌ |
| 12 | Tool: create_columns | Tools | ❌ |
| 13 | Tool: add_database_items | Tools | ❌ |
| 21 | Tracker 패턴 (습관, 독서, 목표) | Patterns | ❌ |
| 25 | WebSocket Chat (/ws/chat) | Routers | ❌ |
| 26 | Template REST API (/api/templates/*) | Routers | ❌ |
| 29 | 채팅 인터페이스 | Frontend | ❌ |
| 30 | 진행률 표시 | Frontend | ❌ |

**산출물**: 채팅으로 5가지 기본 템플릿 생성 (습관 트래커, 프로젝트 보드, 독서 기록, 회의록, 간단한 CRM)

---

### Phase 2: 고도화 (Week 4~5) — 10개 기능

**목표**: 중첩 페이지 + 색상 테마 + 패턴 라이브러리

| # | 기능 | 모듈 | 상태 |
|---|------|------|------|
| 4 | 구조화된 로깅 | Core | ❌ |
| 8 | Blueprint Validator (JSON 검증) | Agent | ❌ |
| 14 | Tool: apply_color_theme | Tools | ❌ |
| 15 | Tool: link_databases (Relation) | Tools | ❌ |
| 20 | Dashboard 패턴 | Patterns | ❌ |
| 22 | Bookmark 패턴 | Patterns | ❌ |
| 23 | Project Manager 패턴 | Patterns | ❌ |
| 24 | Note Collection 패턴 (Tea Note) | Patterns | ❌ |
| 27 | Pattern API (/api/patterns) | Routers | ❌ |
| 31 | Blueprint 미리보기 UI | Frontend | ❌ |

**산출물**: 이미지 수준의 템플릿 자동 생성 (대시보드, 북마크, Tea Note)

---

### Phase 3: 완성 & 배포 (Week 6~7) — 8개 기능

**목표**: 프로덕션 수준 완성 + 배포

| # | 기능 | 모듈 | 상태 |
|---|------|------|------|
| 16 | Tool: generate_cover (AI 이미지) | Tools | ❌ |
| 32 | 반응형 + 다크모드 | Frontend | ❌ |
| 33 | Unit Tests (80%+) | Test | ❌ |
| 34 | Integration Tests | Test | ❌ |
| 35 | E2E Tests | Test | ❌ |
| 36 | GitHub Actions CI | Infra | ❌ |
| 37 | Vercel 배포 | Infra | ❌ |
| 38 | Railway 배포 | Infra | ❌ |

**산출물**: 배포된 웹 서비스 + 완성된 오픈소스 레포

---

### Phase 4: 발표 & 오픈소스화 (Week 8)

| 항목 | 상태 |
|------|------|
| 시연 영상 제작 (3분) | ❌ |
| 가짜연구소 발표 자료 | ❌ |
| GitHub 정리 (README, Contributing, License) | ❌ |
| 블로그 포스트 (개발 과정 회고) | ❌ |
| 커뮤니티 공유 (Reddit, Twitter, 노션 한국 커뮤니티) | ❌ |

---

## 4. 진행률 요약

| Phase | 총 기능 | 완료 | 진행률 |
|-------|---------|------|--------|
| Phase 0 | 8 | 0 | 0% |
| Phase 1 | 13 | 0 | 0% |
| Phase 2 | 10 | 0 | 0% |
| Phase 3 | 8 | 0 | 0% |
| **전체** | **39** | **0** | **0%** |
