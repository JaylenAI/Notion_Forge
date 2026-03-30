# 진행 현황 (Current Status)

> 최종 업데이트: 2026-03-30
> 현재 브랜치: dev-2

---

## 전체 진행률

```
Notion API 기능         [██████████] 100%  74개
AI 스킬 시스템          [██████████] 100%  7개 스킬
DB 생성 + 샘플 데이터   [██████████] 100%  5/5 성공
프론트엔드 UI           [██████████] 100%  노션 스타일 렌더러
테스트                  [██████████] 100%  39/39
```

---

## 완료 기능

### AI Agent
- ✅ 7개 행위 기반 스킬 (track/collect/manage/plan/organize/guide/hub)
- ✅ AI Tool Calling (Groq gpt-oss-120b / Gemini / Claude)
- ✅ 유저 맥락 맞춤 (운동→운동 속성, 독서→독서 속성)
- ✅ 스마트 폴백 (AI 실패 시 키워드 기반 맥락 감지)
- ✅ 타입 별칭 자동 변환 (text→rich_text, person→rich_text)

### Notion API (74개)
- ✅ 블록 30+, 인라인 서식 12, 미디어 7, 고급 7, 임베드 12
- ✅ DB 뷰 10개 (Views API + data_source_id)
- ✅ DB 속성 15+ 타입 + 샘플 데이터 자동 삽입
- ✅ Search/Comments/Markdown/Lock/Archive API
- ✅ Legacy API (2022-06-28) 호환

### 프론트엔드
- ✅ 레퍼런스 #1 다크 테마 (Dashboard/Library/Integrations/Profile/Support)
- ✅ 노션 스타일 렌더러 (callout, heading, DB 테이블, 뷰 탭, 체크리스트)
- ✅ PREVIEW 토글 (노션 렌더링 ↔ 스키마 뷰)
- ✅ 로고 → 홈, NEW TEMPLATE → 초기화, 상단 아이콘 동작
- ✅ WebSocket 채팅 + REST 폴백

---

## 남은 것

| 항목 | 담당 |
|------|------|
| AI 모델 업그레이드 | 사용자 (API 키 제공 예정) |
| 프론트엔드 세부 디자인 튜닝 | 추후 |
| Vercel + Railway 배포 | 추후 |
| 시연 영상 + 발표 자료 | 사용자 (직접 준비) |

---

## 접속

| 서비스 | URL |
|--------|-----|
| Frontend | http://localhost:9501 |
| Backend | http://localhost:9500 |
| Swagger | http://localhost:9500/docs |
| GitHub | https://github.com/JaylenAI/notion_ai_agent/tree/dev-2 |
