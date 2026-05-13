# dev-2 브랜치 개발 계획

> AI Tool Calling 기반 스킬 시스템으로 전환
> 브랜치: dev-2
> 최종 업데이트: 2026-03-27

---

## 핵심 변경

```
dev (기존): 하드코딩 7개 함수 → 유저 맥락 무시, 항상 같은 결과
dev-2 (변경): AI Tool Calling + 스킬 .md → 유저 맥락 맞춤 템플릿
```

## 변경 파일

| 파일 | 상태 |
|------|------|
| `agent/blueprint_generator.py` | ✅ 재작성 (AI Tool Calling) |
| `skills/` 폴더 전체 | ✅ 재작성 (7개 스킬, 공식 플러그인 패턴) |
| `skills/__init__.py` | ✅ 수정 (새 구조 로더) |
| `agent/orchestrator.py` | ✅ 미세 수정 (새 generator 연결) |
| 그 외 모든 파일 | ❌ 변경 없음 |

## 개발 Phase

### Phase 1: 스킬 .md 7개 작성 — ✅ 완료 (2026-03-27)
```
skills/
├── track/SKILL.md + examples/ + reference/
├── collect/SKILL.md + examples/ + reference/
├── manage/SKILL.md + examples/ + reference/
├── plan/SKILL.md + examples/ + reference/
├── organize/SKILL.md + examples/ + reference/
├── guide/SKILL.md + examples/ + reference/
└── hub/SKILL.md + examples/ + reference/
```
- 7개 SKILL.md 작성 완료
- Sample Data Requirements 섹션 추가
- auto_discover_skills() 자동 검색 함수 추가

### Phase 2: blueprint_generator.py 재작성 — ✅ 완료 (2026-03-27)
- 시스템 프롬프트 + Tool 스키마 정의
- AI 1회 호출 → 스킬 선택 + 내용 생성
- 스킬 .md 구조 + AI 내용 → Blueprint JSON 조립
- 기존 하드코딩은 폴백으로 유지
- CRITICAL SAMPLE DATA RULES 추가 (샘플 데이터 품질 강화)

### Phase 3: 연결 + 테스트 — ✅ 완료 (2026-03-27)
- Orchestrator 연결
- 다양한 질문 테스트
- 기존 38개 테스트 통과 확인
- 실제 Notion E2E 테스트

---

## 안 바뀌는 것
- notion/client.py (74개 API)
- notion/block_builder.py (전체 블록)
- agent/tools/* (8개 Tool)
- routers/*, schemas/*, frontend/*
- Docker, Makefile, tests/

### Phase 4: 핵심 버그 수정 — ✅ 완료 (2026-03-30)
- notion-client SDK 3.0 (2025-09-03)에서 DB properties 빈 객체 반환 문제
- 해결: DB 생성/조회/항목 삽입을 Legacy API (2022-06-28)로 전환
- 결과: 속성 7개 + 샘플 5개 + 뷰 3개 모두 정상 생성 확인

---

## 남은 것
- ❌ 프론트엔드 디자인 레퍼런스 적용 (사용자 제공 대기)
- ❌ 시연 영상 + 발표 자료 (사용자 직접 준비)
- ❌ Vercel + Railway 배포
- ❌ 새 스킬 추가 (필요시)
