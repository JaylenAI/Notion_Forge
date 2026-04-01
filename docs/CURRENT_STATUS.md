# 진행 현황 (Current Status)

> 최종 업데이트: 2026-04-01
> 현재 브랜치: dev-2

---

## 전체 진행률

```
Notion API 74개 기능    [██████████] 100%
AI 자유 설계 시스템      [██████████] 100%
AI 프로 디자인 시스템    [██████████] 100%
스킬 시스템 12개        [██████████] 100%
프론트엔드 UI 5페이지   [██████████] 100%
NotionRenderer 14블록  [██████████] 100%
Library 수동 저장       [██████████] 100%
테스트 39/39           [██████████] 100%
프론트엔드 UI/UX 고도화 [█████████░]  90%
페이지 전체 너비        [██████████] 100%
링크드 DB 뷰           [██████████] 100%
```

---

## 완료 기능

### AI Agent
- ✅ AI 자유 설계 (blocks[] + databases[] 모두 AI가 결정)
- ✅ 12개 스킬 (track/collect/manage/plan/organize/guide/hub/finance/journal/content/learn/crm)
- ✅ 4개 AI 프로바이더 (Gemini/Groq/Claude/OpenAI)
- ✅ 동적 모델 선택 (API로 모델 목록 조회)
- ✅ 스마트 폴백 6개 (AI 실패 시 키워드 기반)
- ✅ 실시간 스트리밍 (매 단계 WebSocket)

### AI 프로 디자인 시스템 (v5.1.0)
- ✅ 시스템 프롬프트 전면 재작성 (Thomas Frank/Easlo 수준 디자인 규칙 50+개)
- ✅ 색상 팔레트 2-3색 제한 규칙 (스킬별 추천 팔레트 7종)
- ✅ 대시보드 컬럼 레이아웃 30/70 분할 필수화 (width_ratio 지원)
- ✅ 정보 계층 구조 강제 (callout→spacing→columns→DB→toggle)
- ✅ 아마추어 안티패턴 10가지 방지 규칙
- ✅ DB 뷰-속성 자동 매칭 규칙 (status→board, date→calendar 등)
- ✅ 커버 이미지 20개 (색상 10 + 카테고리 10: business/fitness/study 등)
- ✅ 12개 스킬 전체에 Pro Design Guide 섹션 추가

### Notion API (74개 + 확장)
- ✅ 블록 30+ 종, 인라인 서식 전체, 미디어 전체
- ✅ DB 뷰 10종 (Views API + data_source_id)
- ✅ 샘플 데이터 자동 삽입 (5개+)
- ✅ TYPE_ALIASES 17개, Legacy API 호환
- ✅ 컬럼 width_ratio 지원 (30/70 대시보드 분할)
- ✅ **페이지 전체 너비 자동 설정** (Internal API, token_v2)
- ✅ **링크드 DB 뷰 생성** (Views API create_database)

### 프론트엔드 (기본)
- ✅ 다크 테마 5페이지 (Dashboard/Library/Integrations/Profile/Support)
- ✅ 프롬프트 스타터 카드 6개 (원클릭 생성)
- ✅ NotionRenderer: 14개 블록 + 4개 DB 뷰 (Table/Board/Calendar/Gallery)
- ✅ Library 수동 저장 (Save to Library 버튼, 중복 방지)
- ✅ 완료 후 액션 버튼 (Open in Notion + Save to Library + Copy URL + Create Another)
- ✅ 에러 상태 UI
- ✅ UI 영어 통일
- ✅ Mock 데이터 완전 제거 → 실제 데이터 연동

### 프론트엔드 UI/UX 고도화 (v5.0.0)
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
- ✅ StatusBar 사이드바 오프셋 (사이드바에 가려지지 않음)
- ✅ 사이드바 footer StatusBar 겹침 방지 (pb-14)
- ✅ 미리보기 패널 오버플로우 수정
- ✅ PRO PLAN 카드 제거, Support를 nav 항목으로 이동
- ✅ Library 자동 저장 → 수동 저장 (Save to Library 버튼)

### 테스트
- ✅ 39/39 통과 (28 unit + 10 integration + 1)
- ✅ 실제 Notion 생성 QA 8건 전부 성공

---

## 개발 예정 (UI/UX)

| 항목 | 상태 | 설명 |
|------|------|------|
| 드래그 앤 드롭 블루프린트 재배치 | ❌ 미개발 | LivePreview에서 DB/서브페이지 카드 드래그 순서 변경 |
| 즐겨찾기 퀵 액세스 | ❌ 미개발 | 사이드바에 starred 템플릿 최대 5개 바로가기 |
| 블루프린트 JSON 내보내기/가져오기 | ❌ 미개발 | LivePreview 툴바에서 Export/Import 버튼 |
| 실시간 연결 품질 모니터 | ❌ 미개발 | WebSocket ping/pong latency 실측 + StatusBar 표시 |

---

## 남은 것 (기타)

| 항목 | 상태 | 비고 |
|------|------|------|
| AI 블록 다양성 강화 | 🔄 진행 예정 | quote/code/column 적극 활용 |
| AI 모델 업그레이드 | 대기 | Claude/GPT-4o = 더 복잡한 구조 |
| 배포 (Vercel + Railway) | 대기 | |
| 시연 영상 + 발표 | 대기 | 사용자 직접 준비 |
