# Skill Development Guide

> 최종 업데이트: 2026-05-18
> 버전: v0.1.6 | 48개 스킬 등록 완료
>
> NotionForge 스킬 개발 가이드 — 새 스킬을 만들고 등록하는 방법을 설명합니다.

---

## 1. 스킬이란?

스킬(Skill)은 NotionForge가 특정 유형의 Notion 템플릿을 생성할 때 사용하는 구조 가이드입니다.

사용자가 "운동 추적기 만들어줘"라고 요청하면:
1. AI가 요청을 분석하여 가장 적합한 스킬(예: `track`)을 선택
2. 해당 스킬의 `SKILL.md`를 로드하여 구조 가이드로 활용
3. AI 생성 내용 + 스킬 구조 = Blueprint JSON 조립
4. Orchestrator가 Blueprint를 실행하여 Notion 페이지 생성

스킬은 코드가 아니라 **마크다운 문서**입니다. Python을 몰라도 새 스킬을 만들 수 있습니다.

---

## 2. 파일 구조

```
backend/app/skills/
├── __init__.py          # 스킬 레지스트리 + 로더
├── track/               # 스킬 디렉토리 (이름 = 스킬 ID)
│   ├── SKILL.md         # [필수] 구조 가이드
│   ├── examples/        # [권장] AI 참고용 예제
│   │   ├── exercise.md
│   │   └── study.md
│   └── reference/       # [선택] 상세 가이드
│       └── properties.md
├── collect/
│   ├── SKILL.md
│   ├── examples/
│   └── reference/
└── (your_skill)/
    ├── SKILL.md
    ├── examples/
    └── reference/
```

### 각 파일의 역할

| 파일 | 필수 | 설명 |
|------|------|------|
| `SKILL.md` | 필수 | 템플릿 구조, 레이아웃, DB 설계, 샘플 데이터 규칙 |
| `examples/*.md` | 권장 | 실제 사용 예제 (AI가 참고) |
| `reference/*.md` | 선택 | 속성 타입별 상세 가이드 |

---

## 3. SKILL.md 템플릿

아래 템플릿을 복사하여 새 스킬의 `SKILL.md`를 작성하세요.

```markdown
---
name: your_skill_name
description: 한 줄 설명 (영문). 어떤 템플릿을 생성하는지.
---

# Skill Name (한글 이름)

한 문단으로 스킬이 하는 일을 설명합니다.

## Quick Start

1. **맥락 파악**: 사용자가 무엇을 원하는지
2. **속성 설계**: 필수 속성 + 맥락별 속성
3. **레이아웃 설정**: Single column / Two-column
4. **뷰 추가**: 주요 뷰 타입 결정
5. **샘플 생성**: 최소 5개, 모든 속성값 포함

## Template Structure

### Layout
(Single column / Two-column 설명)

### Block Order
1. callout: ...
2. divider
3. heading_1: ...
4. database_ref: ...
5. (등등)

### Database Design

Required properties:
- title: 항목 이름
- (필수 속성들)

Context-dependent properties:
- (맥락에 따라 AI가 결정하는 속성들)

### Views
- Required: (주요 뷰)
- Optional: (선택 뷰)

### Sub-Pages
(하위 페이지 규칙)

### Sample Data
(샘플 데이터 생성 규칙 - 아래 Sample Data Requirements 참조)

## Content Adaptation Examples

**예시 1**: Properties -> ...
**예시 2**: Properties -> ...

## Formatting Rules

- (서식 규칙들)

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within +/-2 weeks
- Status values: spread across all statuses (시작 전, 진행 중, 완료)
- Select values: use different options for variety
- Number values: use realistic, varied numbers
- Checkbox: mix of true and false
```

---

## 4. 샘플 데이터 규칙 (필수)

이 섹션이 가장 중요합니다. AI가 생성하는 템플릿의 품질은 샘플 데이터에 달려 있습니다.

### 필수 규칙

1. **최소 3-5개 샘플 항목** 생성
2. **모든 속성값 채우기** - title과 icon만 있으면 안 됩니다
3. **뷰 타입에 맞는 속성 필수 포함**:
   - Calendar 뷰 → 날짜 속성 필수
   - Board 뷰 → 상태 속성 필수
   - Gallery 뷰 → 아이콘/커버 필수

### 나쁜 예시 (이렇게 하면 안 됩니다)

```json
[
  {"이름": "항목1", "icon": "📌"},
  {"이름": "항목2", "icon": "📌"},
  {"이름": "항목3", "icon": "📌"}
]
```

문제점:
- title과 icon만 있고 나머지 속성값이 없음
- 아이콘이 모두 같음 (다양성 부족)
- 날짜, 상태, 카테고리 등 핵심 속성 누락
- Calendar 뷰에서 빈 캘린더가 표시됨
- Board 뷰에서 모든 항목이 "미분류"에 몰림

### 좋은 예시 (이렇게 해야 합니다)

```json
[
  {
    "운동명": "러닝 30분",
    "종류": "유산소",
    "시간": 30,
    "칼로리": 300,
    "날짜": "2026-04-01",
    "완료": true,
    "icon": "🏃"
  },
  {
    "운동명": "스쿼트 5세트",
    "종류": "근력",
    "시간": 40,
    "칼로리": 250,
    "날짜": "2026-04-02",
    "완료": false,
    "icon": "🏋️"
  },
  {
    "운동명": "요가 기초",
    "종류": "유연성",
    "시간": 50,
    "칼로리": 150,
    "날짜": "2026-04-03",
    "완료": true,
    "icon": "🧘"
  },
  {
    "운동명": "수영 자유형",
    "종류": "유산소",
    "시간": 60,
    "칼로리": 500,
    "날짜": "2026-04-04",
    "완료": false,
    "icon": "🏊"
  },
  {
    "운동명": "벤치프레스 3세트",
    "종류": "근력",
    "시간": 35,
    "칼로리": 200,
    "날짜": "2026-04-05",
    "완료": false,
    "icon": "💪"
  }
]
```

장점:
- 모든 db_properties 값이 채워져 있음
- 아이콘이 항목마다 다름
- 날짜가 실제 날짜 (Calendar 뷰에 표시됨)
- 종류(select)가 다양하게 분포
- 완료(checkbox)가 true/false 혼합
- 숫자값이 현실적이고 다양함

### 뷰 타입별 필수 속성

| 뷰 타입 | 반드시 포함해야 할 속성 | 이유 |
|---------|----------------------|------|
| Calendar | date (실제 날짜값) | 날짜 없으면 캘린더가 비어 보임 |
| Board | status (다양한 상태) | 상태 없으면 모든 항목이 한 열에 몰림 |
| Gallery | icon (다양한 아이콘) | 아이콘 없으면 카드가 밋밋함 |
| Timeline | date (시작일 + 종료일) | 타임라인에 바가 표시되려면 날짜 필수 |
| Table | 모든 속성 | 빈 셀이 많으면 불완전해 보임 |

---

## 5. 스킬 등록 방법

### 방법 1: 자동 검색 (권장)

`__init__.py`의 `auto_discover_skills()` 함수가 `SKILL.md` 파일이 있는 디렉토리를 자동으로 검색합니다.
새 스킬 디렉토리에 `SKILL.md`를 넣으면 자동으로 인식됩니다.

### 방법 2: 수동 등록

`backend/app/skills/__init__.py`의 `SKILL_REGISTRY`에 직접 추가:

```python
SKILL_REGISTRY: dict[str, dict[str, str]] = {
    # ... 기존 스킬들 ...
    "your_skill": {
        "name": "your_skill",
        "description": "Description of what this skill creates",
        "keywords": "키워드1,키워드2,키워드3",
    },
}
```

### blueprint_generator.py에 빌더 함수 추가

`backend/app/agent/blueprint_generator.py`에 빌더 함수를 추가합니다:

```python
def _build_your_skill(bp: dict, c: dict, bg: str) -> None:
    """Your Skill 구조: callout -> heading -> DB -> FAQ"""
    bp["blocks"] = [
        {"type": "callout", "text": c.get("callout_text", ""), "icon": c.get("icon", "📋"), "color": bg},
        {"type": "divider"},
        {"type": "heading_1", "text": c.get("db_name", "Items"), "color": bg},
        {"type": "database_ref", "db_index": 0},
        {"type": "divider"},
    ]
    for faq in c.get("faq", []):
        bp["blocks"].append({"type": "toggle", "text": faq["q"], "children_text": faq["a"]})

    _add_database(bp, c)
```

그리고 `SKILL_BUILDERS` 딕셔너리에 등록:

```python
SKILL_BUILDERS = {
    # ... 기존 빌더들 ...
    "your_skill": _build_your_skill,
}
```

---

## 6. 테스트 체크리스트

새 스킬을 만든 후 아래 항목을 모두 확인하세요:

### 파일 구조
- [ ] `backend/app/skills/{skill_name}/SKILL.md` 파일 존재
- [ ] SKILL.md frontmatter에 `name`과 `description` 포함
- [ ] `examples/` 디렉토리에 최소 1개 예제 파일
- [ ] SKILL.md에 Sample Data Requirements 섹션 포함

### 등록
- [ ] `SKILL_REGISTRY`에 스킬 등록 또는 `auto_discover_skills()`로 자동 검색 확인
- [ ] `SKILL_BUILDERS`에 빌더 함수 등록
- [ ] `load_skill(skill_name)`으로 SKILL.md 로드 확인

### 샘플 데이터
- [ ] 최소 5개 샘플 항목 생성
- [ ] 모든 db_properties 값이 채워져 있음
- [ ] Calendar 뷰 사용 시 date 속성에 실제 날짜값 포함
- [ ] Board 뷰 사용 시 status 속성이 다양한 상태로 분포
- [ ] Gallery 뷰 사용 시 icon이 항목마다 다름
- [ ] Select 속성이 다양한 옵션으로 분포
- [ ] Number 속성이 현실적이고 다양한 숫자
- [ ] Checkbox 속성이 true/false 혼합

### 기능 테스트
- [ ] Mock 모드에서 키워드 매칭으로 스킬 선택됨
- [ ] AI 모드에서 적절한 프롬프트로 스킬 선택됨
- [ ] Blueprint JSON이 올바르게 생성됨
- [ ] Orchestrator가 Blueprint를 정상 실행
- [ ] Notion에 실제 페이지 생성 확인
- [ ] 생성된 DB의 뷰가 올바르게 표시됨
- [ ] 샘플 데이터가 모든 뷰에서 잘 보임

### 품질 확인
- [ ] 기존 테스트 전체 통과 (1215개)
- [ ] 다른 스킬의 키워드와 충돌 없음
- [ ] SKILL.md가 800줄 이하
