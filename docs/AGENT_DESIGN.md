# AI Agent 설계 (Agent Design)

> 최종 업데이트: 2026-05-13
> 버전: v8.1.0

---

## 1. Agent 아키텍처

### 전체 구조

```
┌──────────────────────────────────────────────────────────────┐
│                    Agent Orchestrator                         │
│                                                              │
│  ┌──────────────┐   ┌───────────────┐   ┌────────────────┐  │
│  │   Input       │   │   Intent      │   │    Skill       │  │
│  │  Guardrail   │──→│  Analyzer     │──→│   Router       │  │
│  │ (인젝션방어)  │   │ (의도+레이아웃)│   │ (48개 스킬)    │  │
│  └──────────────┘   └───────────────┘   └───────┬────────┘  │
│                                                  │           │
│  ┌───────────────────────────────────────────────▼────────┐  │
│  │              Blueprint Generator                       │  │
│  │  PromptAssembler → LLM → QualityValidator → PostProc   │  │
│  │              (Gen-Eval 루프, 최대 3회)                   │  │
│  └───────────────────────────────────┬────────────────────┘  │
│                                      │                       │
│  ┌──────────────────┐   ┌───────────▼──────────┐            │
│  │  Approval Gate   │←──│  Creation Executor   │            │
│  │  (사용자 확인)    │   │  (5-Pass 생성)       │            │
│  └──────────────────┘   └───────────┬──────────┘            │
│                                      │                       │
│              ┌───────────────────────┼───────────────┐       │
│              ▼           ▼           ▼               ▼       │
│         ┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│         │ Page   │ │ Database │ │  Block   │ │  View    │  │
│         │ Tools  │ │  Tools   │ │  Tools   │ │  Tools   │  │
│         └────────┘ └──────────┘ └──────────┘ └──────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Provider Router (Circuit Breaker + Fallback Chain)   │    │
│  │  Copilot SDK ↔ Claude ↔ Gemini ↔ Groq ↔ OpenAI      │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

### 처리 파이프라인 (6단계)

```
Step 1: Input Guardrail
  └─ 메시지 검증 (길이, 인젝션 패턴 13종, 스팸 감지)
  └─ risk_level: none / low / medium / high

Step 2: Intent Analysis + Layout Routing
  └─ 의도 분류: CREATE / MODIFY / QUESTION
  └─ 레이아웃 감지: 8종 (dashboard, kanban, calendar, gallery, ...)
  └─ 복잡도 판단: simple / standard / advanced

Step 3: Skill Routing
  └─ 키워드 빠른경로 (0ms) + LLM 정밀경로 (필요시)
  └─ 48개 스킬 중 최적 매칭 (Tier2 우선)

Step 4: Blueprint Generation (Gen-Eval Loop)
  └─ PromptAssembler: base.md + mode + layout + views_catalog + golden
  └─ LLM 생성 → QualityValidator 3계층 검증
  └─ 불합격 시 에러 피드백 주입 → 재생성 (최대 3회)
  └─ PostProcessor: 13종 자동 수정

Step 5: Approval Gate + Creation
  └─ 사용자 확인 대기 (60초 타임아웃)
  └─ 5-Pass 생성:
      Pass 1: 메인 페이지 (아이콘/커버)
      Pass 2: 데이터베이스 (속성 + Relation)
      Pass 3: 블록 (중첩 구조)
      Pass 4: 뷰 (configuration)
      Pass 5: 샘플 데이터 + 서브페이지

Step 6: Validation + Rollback
  └─ 생성 결과 검증 (기대 블록/DB 수 vs 실제)
  └─ 실패 시 자동 롤백 (생성된 리소스 삭제)
```

---

## 2. 에러 복구 — 6계층 방어

```
Layer 1: Input Guardrail      — 프롬프트 인젝션 차단 (13 regex)
Layer 2: Gen-Eval Loop         — AI 출력 품질 보장 (3회 재시도 + 전략 변경)
Layer 3: Circuit Breaker       — AI Provider 장애 대응 (3회 실패 → 차단 → 120초 복구)
Layer 4: Notion API Retry      — 429/502/503 재시도 (지수 백오프)
Layer 5: Agent Reflection      — 도구 실행 실패 → AI 반성 → 수정된 인자로 재시도
Layer 6: Transaction Rollback  — 전체 생성 실패 → 부분 결과 삭제
```

---

## 3. 프롬프트 엔지니어링

### 모듈화 구조

```
app/agent/prompts/
├── base.md                 # 핵심 철학 + 블록 타입 + 디자인 규칙
├── modes/
│   ├── simple.md           # 15블록 이하, 1-2 DB
│   ├── standard.md         # 20-30블록, 2-3 DB, Formula OK
│   └── advanced.md         # 30-50블록, 3-4 DB, 차트/대시보드
├── layouts/
│   ├── kanban_board.md
│   ├── dashboard_widgets.md
│   ├── calendar_main.md
│   ├── gallery_hero.md
│   └── ...                 # 8종
├── views_catalog.md        # 뷰 6종 configuration 가이드
├── relations.md            # Relation/Formula/Rollup 패턴
├── design_tokens.md        # 색상 팔레트, 간격 규칙
└── golden/                 # Few-shot 예제 (JSON)
    ├── simple_tracker.json
    ├── kanban_board.json
    ├── dashboard_widgets.json
    └── ...                 # 8종
```

### 동적 조립 규칙

```python
prompt = base.md                      # 항상 포함
prompt += modes/{complexity}.md       # 복잡도별
prompt += layouts/{layout}.md         # 레이아웃별 (있으면)
prompt += views_catalog.md            # 뷰 옵션
prompt += relations.md                # Relation 패턴
prompt += golden/{layout}.json        # Few-shot 예제

# 프롬프트 크기 > max_chars 시 압축 모드 전환
```

### 핵심 철학

```
"Match the user's intent — no more, no less."

- "물 마신 양 기록" → 1 DB + table 뷰. 과하게 만들지 않는다.
- "창업 대시보드" → 멀티 DB + 리치 뷰 + 링크드뷰 + 차트.
- AI의 역할은 적절한 복잡도를 판단하는 것.
```

---

## 4. Tool Registry (9개 도구)

| # | Tool | 설명 | LLM Function Calling 스펙 |
|---|------|------|--------------------------|
| 1 | `create_page` | 페이지 생성 (아이콘/커버) | title, icon, cover_url, parent_id |
| 2 | `create_database` | DB 생성 + 속성 설정 | title, properties, is_inline |
| 3 | `add_blocks` | 블록 추가 (중첩 지원) | page_id, blocks[] |
| 4 | `create_view` | 뷰 생성 (6종 + config) | db_id, view_type, config |
| 5 | `add_sample_data` | DB 샘플 항목 추가 | db_id, items[] |
| 6 | `create_sub_page` | 서브페이지 생성 | parent_id, title, blocks[] |
| 7 | `modify_template` | 기존 템플릿 수정 | page_id, modifications |
| 8 | `link_databases` | DB 간 Relation 설정 | source_db, target_db |
| 9 | `generate_cover` | 커버 이미지 URL 생성 | category, theme |

### Agent Loop 실행 흐름

```
AI가 도구 선택 (function calling)
  → Tool Registry에서 도구 조회
  → 인자 검증 + 실행
  → 결과를 AI에 반환
  → AI가 다음 도구 선택 또는 완료
  → 실패 시: AI가 에러 분석 → 수정된 인자로 재시도
```

---

## 5. QualityValidator — 3계층 검증

### 검증 구조

```
Layer 1: Schema Validation (가중치 50%)
  ├─ title 필드 존재
  ├─ blocks[] 비어있지 않음
  ├─ databases[] 비어있지 않음
  ├─ 블록 타입 유효성 (20종)
  ├─ database_ref에 db_index 존재
  ├─ db_index 범위 내
  ├─ column_list 안에 database_ref 없음 (Critical)
  ├─ DB에 title 속성 존재
  ├─ 속성 타입 유효성
  └─ Relation/Formula/Rollup 정합성

Layer 2: Content Validation (가중치 30%)
  ├─ 샘플 항목 3개 이상
  ├─ 중복 제목 없음
  ├─ 제목 길이 적절
  ├─ Status 값 다양성
  ├─ 빈 텍스트 블록 비율 제한
  └─ 서브페이지 제목 존재

Layer 3: Design Validation (가중치 20%)
  ├─ 첫 블록 = callout (환영 메시지)
  ├─ heading 블록 존재 (섹션 구조)
  ├─ 색상 일관성 (배경색 테마)
  ├─ 연속 동일 블록 없음
  ├─ 서브페이지 아이콘 존재
  └─ database_ref가 첫 3블록에 없음

합격 기준: total_score >= 60 AND critical_issues == 0
```

### PostProcessor 자동 수정 (13종)

```
1.  welcome callout 보장 (없으면 추가)
2.  guide toggle 보장 (하단)
3.  column_list 안 database_ref → 페이지 레벨로 이동
4.  섹션 간 spacing paragraph 삽입
5.  database_ref 참조 유효성 검증
6.  Status 값 한글화
7.  샘플 항목 최소 3개 보장
8.  샘플 아이콘 추가
9.  cover_category 보장
10. 서브페이지 아이콘 추가
11. table_of_contents 라벨링
12. 뷰 속성 검증
13. 디자인 다양성 강화
```

---

## 6. Provider Strategy Pattern

### 아키텍처

```
ProviderRouter
  ├─ CircuitBreaker (provider별 상태 관리)
  │    ├─ threshold: 3회 연속 실패 → 회로 개방
  │    ├─ reset: 120초 후 half-open
  │    └─ 상태: closed → open → half-open → closed
  │
  └─ Fallback Chain
       ├─ 1순위: Copilot SDK (기본)
       ├─ 2순위: Claude (높은 품질)
       ├─ 3순위: Gemini (대용량)
       ├─ 4순위: Groq (빠른 응답)
       └─ 5순위: OpenAI (범용)
```

### Provider 인터페이스

```python
class BaseProvider:
    name: str
    supports_json_mode: bool
    supports_function_calling: bool

    async def call(system_prompt, user_message, model) -> dict | None
    async def call_with_tools(system_prompt, user_message, tools, model) -> dict | None
    def extract_json(text) -> dict | None
```

---

## 7. Notion API 커버리지

### 블록 타입 (20종)

```
heading_1, heading_2, heading_3, paragraph, callout, quote,
toggle, bulleted_list_item, numbered_list_item, to_do,
divider, table_of_contents, column_list, database_ref,
linked_view, image, bookmark, embed, code, tab
```

### 뷰 타입 (6종 + 실험적 1종)

```
table, board, calendar, gallery, list, timeline, chart(실험적)
```

### 속성 타입 (17종)

```
title, rich_text, number, select, multi_select, status, date,
people, files, checkbox, url, email, phone_number,
formula, relation, rollup, created_time, last_edited_time
```
