# 진행 현황 (Current Status)

> 최종 업데이트: 2026-04-01
> 현재 브랜치: dev-2

---

## 전체 진행률

```
Notion API 74개 기능    [██████████] 100%
AI 자유 설계 시스템      [██████████] 100%
프론트엔드 UI           [██████████] 100%
AI 모델 선택            [██████████] 100%
테스트 39/39            [██████████] 100%
```

---

## 현재 시나리오 (유저 플로우)

### 1. 접속 + 설정
```
유저 → http://localhost:9501 접속
     → Integrations 페이지
     → Notion API Key + Page ID 입력
     → AI API Key 입력 (Gemini/Groq/Claude/OpenAI)
     → 프로바이더 자동 감지 + 모델 목록 로드
     → 모델 선택 + 저장
```

### 2. 템플릿 생성 (간단)
```
유저: "카페 메뉴판 만들어줘"
  ↓
AI 분석 → collect 스킬 선택
  ↓
AI 설계 → blocks 7개 + DB 1개 (메뉴명,가격,카테고리,설명)
  ↓
Notion API 실행 → 페이지+DB+샘플5개+뷰2개 생성
  ↓
결과: Notion URL + 미리보기
```

### 3. 템플릿 생성 (복잡)
```
유저: "카페 통합 운영 시스템 만들어줘. 메뉴, 매출, 재고, 직원 전부"
  ↓
AI 분석 → manage 스킬 선택
  ↓
AI 설계 → blocks 20+개 + DB 4개 + 하위 페이지
  ↓
Notion API 실행 → 전체 구조 생성
  ↓
결과: Notion URL + 미리보기
```

### 4. 미리보기
```
우측 패널:
  PREVIEW 모드 → 노션 스타일 렌더링 (callout, DB 테이블, 뷰 탭)
  SCHEMA 모드 → 속성 목록 + 뷰 배지
  완료 시 → Notion 링크 배너
```

---

## 완료 기능

### AI Agent
- ✅ AI 자유 설계 (blocks[] + databases[] 모두 AI가 결정)
- ✅ 유저 요청 복잡도에 비례하는 결과
- ✅ 7개 스킬 (.md 가이드)
- ✅ 4개 AI 프로바이더 (Gemini/Groq/Claude/OpenAI)
- ✅ 동적 모델 선택 (API로 모델 목록 조회)
- ✅ 스마트 폴백 (AI 실패 시 키워드 기반)

### Notion API
- ✅ 74개 기능 (블록, 속성, 뷰, 미디어, API 확장)
- ✅ DB 뷰 10종 (Views API + data_source_id)
- ✅ 샘플 데이터 자동 삽입
- ✅ TYPE_ALIASES (text→rich_text 등 17개)
- ✅ Legacy API 호환

### 프론트엔드
- ✅ 다크 테마 (Dashboard/Library/Integrations/Profile/Support)
- ✅ 노션 스타일 렌더러
- ✅ AI 모델 설정 UI
- ✅ 채팅 헤더 모델 배지
- ✅ WebSocket + REST 폴백

---

## 남은 것

| 항목 | 담당 |
|------|------|
| AI 모델 업그레이드 (좋은 모델) | 사용자 (API 키) |
| 스킬 추가/개선 | 사용자 (SKILL_GUIDE.md 참고) |
| 프론트엔드 세부 튜닝 | 추후 |
| 배포 (Vercel + Railway) | 추후 |
| 시연 영상 + 발표 | 사용자 |
