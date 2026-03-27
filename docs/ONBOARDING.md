# 인수인계 문서 (Onboarding Guide)

> 프로젝트에 새로 합류하는 개발자를 위한 종합 가이드
> 최종 업데이트: 2026-03-27

---

## 1. 프로젝트 개요

### 배경

노션 템플릿 크리에이터가 템플릿을 제작하는 데 평균 2~4시간이 소요됩니다. 반복적인 DB 속성 설정, 블록 배치, 색상 테마 적용 등의 작업을 AI Agent가 자동화하여 **80~90% 시간을 절약**하는 것이 목표입니다.

### 핵심 개념

```
사용자 (자연어) → AI Agent (의도 분석 + 구조 설계) → Notion API (실제 생성) → 완성 URL
```

| 개념 | 설명 |
|------|------|
| **Intent Analyzer** | Claude API로 사용자 요청의 의도를 파악 (CREATE/MODIFY/QUESTION) |
| **Blueprint** | AI가 설계한 템플릿 구조 (JSON). 페이지 계층, DB 스키마, 블록 목록 |
| **Tool** | Agent가 호출하는 도구. 각 Tool이 Notion API 엔드포인트에 매핑 |
| **Pattern** | 사전 정의된 템플릿 패턴 (대시보드, 트래커, 북마크 등) |
| **Color Theme** | 색상 톤 설정 (blue, orange, green 등). Notion의 배경색/텍스트색 매핑 |

---

## 2. 아키텍처 요약

```
Frontend (React + Vite)
  │ WebSocket
  ▼
Backend (FastAPI)
  ├─ /ws/chat          → 채팅 WebSocket
  ├─ /api/templates/*  → REST API
  │
  ├─ Agent Orchestrator
  │   ├─ Intent Analyzer  (Claude API)
  │   ├─ Blueprint Generator (Claude API + Pattern Library)
  │   └─ Tool Router → Tools (8개)
  │       ├─ create_page
  │       ├─ create_database
  │       ├─ add_blocks
  │       ├─ create_columns
  │       ├─ add_database_items
  │       ├─ apply_color_theme
  │       ├─ link_databases
  │       └─ generate_cover
  │
  └─ Notion Client (rate limiter 포함)
       │
       ▼
     Notion API (https://api.notion.com/v1/)
```

---

## 3. 디렉토리 구조

```
NotionForge/
├── README.md                          # 프로젝트 소개 + 빠른 시작
├── .env.example                       # 환경변수 템플릿
├── docs/
│   ├── PLANNING.md                    # 기획서
│   ├── MARKET_RESEARCH.md             # 시장조사
│   ├── USER_SCENARIOS.md              # 유저 시나리오
│   ├── ARCHITECTURE.md                # 기술 아키텍처 (상세)
│   ├── AGENT_DESIGN.md                # AI Agent 설계
│   ├── NOTION_API_ANALYSIS.md         # Notion API 분석
│   ├── API.md                         # 백엔드 API 명세
│   ├── SETUP.md                       # 환경 세팅 가이드
│   ├── DEVELOPMENT_PLAN.md            # 개발 계획 + 모듈별 현황
│   ├── ROADMAP.md                     # 주차별 로드맵
│   ├── TEST_GUIDE.md                  # 테스트 가이드
│   ├── QA_CHECKLIST.md                # QA 체크리스트
│   ├── DEPLOY.md                      # 배포 가이드
│   ├── CURRENT_STATUS.md              # 진행 현황 (실시간)
│   ├── ONBOARDING.md                  # 인수인계 문서 (이 문서)
│   ├── CHANGELOG.md                   # 변경 이력
│   └── RETROSPECTIVE.md              # 회고
├── backend/
│   ├── pyproject.toml
│   ├── main.py                        # FastAPI 진입점
│   ├── config.py                      # 환경변수, 설정
│   ├── agent/                         # AI Agent 핵심
│   │   ├── orchestrator.py            # 메인 오케스트레이터
│   │   ├── intent_analyzer.py         # 의도 분석
│   │   ├── blueprint_generator.py     # 구조 설계
│   │   └── tools/                     # 8개 Tool
│   ├── notion/                        # Notion API 래퍼
│   │   ├── client.py
│   │   ├── rate_limiter.py
│   │   └── block_builder.py
│   ├── patterns/                      # 템플릿 패턴 라이브러리
│   ├── routers/                       # API 라우터
│   └── tests/                         # 테스트
└── frontend/
    ├── package.json
    └── src/
        ├── components/                # React 컴포넌트
        ├── stores/                    # Zustand 상태
        └── api/                       # API 클라이언트
```

---

## 4. 개발 시작하기

### 환경 세팅

→ [SETUP.md](SETUP.md) 참고 (10분 내 완료)

### 핵심 파일 읽기 순서

새로 합류하면 아래 순서로 코드를 읽으세요:

```
1. docs/PLANNING.md          → 프로젝트가 뭔지 이해
2. docs/AGENT_DESIGN.md      → Agent 구조 이해
3. backend/agent/orchestrator.py → 메인 실행 흐름
4. backend/agent/tools/       → 각 Tool이 하는 일
5. backend/notion/client.py   → Notion API 호출 방식
6. docs/CURRENT_STATUS.md     → 현재 어디까지 됐는지
```

### 개발 흐름

```
1. CURRENT_STATUS.md에서 미완료 항목 확인
2. 관련 docs/ 문서 읽기
3. 코드 작성
4. 테스트 실행 (poetry run pytest)
5. CURRENT_STATUS.md 업데이트
6. 커밋 (한글 메시지)
```

---

## 5. 주의사항

### Notion API

- **Rate limit 3 req/s**: rate_limiter.py가 자동 관리하지만, 새 API 호출 시 반드시 이를 통해 호출
- **Integration 연결**: 테스트 시 사용할 Notion 페이지에 Integration이 연결되어 있어야 함
- **블록 100개 제한**: `add_blocks`에서 100개 초과 시 자동 분할되는지 확인
- **뷰 생성 불가**: DB 생성 시 기본 테이블 뷰만 생성됨

### AI Agent

- **프롬프트 변경 시 주의**: intent_analyzer.py의 시스템 프롬프트를 변경하면 의도 분석 결과가 달라질 수 있음. 변경 후 반드시 테스트
- **Blueprint 검증**: AI가 생성한 Blueprint는 반드시 validate 후 실행
- **Tool 의존성**: Tool 실행 순서에 의존성이 있음 (create_page → create_database → add_blocks)

### 코드 컨벤션

- 커밋 메시지: **한글**
- 이뮤터블 패턴 사용 (객체 직접 수정 금지)
- 함수 50줄 이내, 파일 800줄 이내
- 에러 핸들링 필수

---

## 6. 관련 문서 링크

| 필요한 정보 | 문서 |
|------------|------|
| 전체 기획 | [PLANNING.md](PLANNING.md) |
| 시장 분석 | [MARKET_RESEARCH.md](MARKET_RESEARCH.md) |
| 사용 시나리오 | [USER_SCENARIOS.md](USER_SCENARIOS.md) |
| Agent 구조 | [AGENT_DESIGN.md](AGENT_DESIGN.md) |
| API 명세 | [API.md](API.md) |
| Notion API 제한 | [NOTION_API_ANALYSIS.md](NOTION_API_ANALYSIS.md) |
| 테스트 방법 | [TEST_GUIDE.md](TEST_GUIDE.md) |
| 배포 방법 | [DEPLOY.md](DEPLOY.md) |
| 현재 진행률 | [CURRENT_STATUS.md](CURRENT_STATUS.md) |
