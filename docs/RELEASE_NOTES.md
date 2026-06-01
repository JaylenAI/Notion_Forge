# Release Notes (Bilingual EN/KR)

> GitHub Release 본문용 영문/국문 노트. 과거 v0.1.0~v0.1.6은 GitHub Releases 페이지에 반영됨.
> v0.2.0은 릴리스 시점에 아래 내용을 태그 노트로 사용한다.

---

## 🇬🇧 EN — v0.2.0: End-to-End Working (UI + AI Pipeline)

The milestone where the product actually works end-to-end across **both** the UI and the AI pipeline.
Backend **1,461 tests** + frontend Vitest/Playwright E2E + live Notion verification.
(A production-stable 1.0 is intentionally deferred until broader skill/beta validation.)

### Fixed (release-blocking defects found via live & UI verification)
- **AI pipeline relation/rollup aggregation (CRITICAL)** — sample relation values arrive in many shapes (title string, `{db_index,item_index}`, `{title,id}`, lists) but only title strings were handled → 0 links → rollups stuck at 0/None. Now multi-format resolution + single_property two-way **mirroring** so rollups aggregate on either side. (Previously masked because only the deterministic recipe path was verified.)
- **WebSocket "no-op" trap** — when disconnected, sending fell back to a preview-only endpoint (no Notion creation) while looking "successful". Added a disconnected banner, honest messaging, auto-reconnect, and a real UI approval→creation E2E.
- **Provider fallback reliability (CRITICAL)** — an empty-but-truthy copilot response was treated as success, skipping fallback. Now only valid responses (with `databases`) count as success; otherwise cascade copilot→groq→gemini→claude. `_fallback_candidates` is circuit-aware (skips 429-blocked providers), groq-first, and includes copilot.
- Chart `x_axis`/`y_axis` dict crash, Groq/OpenAI json-mode 400, AI-missing-title English default ("My Template"), long-message-as-title, date `{start,end}` dict, duplicate title emoji, CRM recipe `남은일수` formula not computing.

### Added
- Transparent fallback notice — when all AI providers fail and a generic template is used, the user is clearly informed.
- Real UI approval→Notion creation E2E (`frontend/e2e/approval.spec.ts`).

### Changed
- Two-way relations now **single_property + sample-link mirroring** (the prior dual_property approach is dropped; it renamed the other side's relation and broke that side's rollup).
- Removed unused duplicate chat UI (the `MainLayout → ChatWindow` chain).

### Known limitations (honest)
- AI generation depends on provider availability. With the Gemini key quota exhausted (429), it relies on copilot/Groq; if all fail simultaneously it degrades to a generic fallback template (with a clear notice).
- AI-generated sample dates may be in the past, so date formulas can be negative/large (logic is correct).
- Single worker recommended. Some of the 48 skills are not yet live-verified.
- **Not hardcoded**: the normal natural-language path is fully AI-designed (`ai_dynamic`). Hardcoding exists only as (a) an emergency fallback when all providers fail, and (b) a curated recipe gallery.

---

## 🇰🇷 KR — v0.2.0: 전 경로 작동 확정 (UI + AI 파이프라인)

제품이 UI·AI 파이프라인 **양쪽** 전 경로에서 실제로 end-to-end 작동하게 된 마일스톤.
백엔드 **1,461 테스트** + 프론트 Vitest/Playwright E2E + 실제 Notion 라이브 검증.
(production-stable 1.0 선언은 더 넓은 스킬/베타 검증 후로 의도적 보류.)

### 수정 (라이브·UI 검증에서 발견한 릴리스 차단급 결함)
- **AI 파이프라인 relation/rollup 집계 (CRITICAL)** — sample relation 값이 제목 문자열·`{db_index,item_index}`·`{title,id}`·리스트 등 다양하게 오는데 제목 문자열만 처리해 링크 0건 → rollup 0/None. 다포맷 해석 + single_property 양방향 **미러링**으로 어느 쪽 rollup이든 집계. (그동안 결정적 recipe 경로만 검증돼 가려져 있었음)
- **WebSocket 무생성 함정** — 미연결 시 미리보기 전용 엔드포인트(Notion 미생성)로 폴백하며 "성공"처럼 보이던 문제 → 미연결 배너 + 정직한 안내 + 자동 재연결 + 실제 UI 승인→생성 E2E.
- **provider 폴백 신뢰성 (CRITICAL)** — copilot의 빈 truthy 응답을 성공으로 처리해 폴백을 건너뛰던 결함 → 유효(databases 존재) 응답만 성공으로 보고 copilot→groq→gemini→claude 캐스케이드. `_fallback_candidates` circuit-aware(429 차단 건너뜀)·groq 우선·copilot 포함.
- 차트 `x_axis`/`y_axis` dict 크래시, Groq/OpenAI json 모드 400, AI 무title 영어 기본값("My Template"), 긴 메시지 제목화, 날짜 `{start,end}` dict, 제목 이모지 중복, CRM recipe `남은일수` formula 미계산.

### 추가
- 전 provider 실패로 generic 폴백을 쓸 때 사용자에게 명확히 고지.
- 실제 UI 승인→Notion 생성 E2E(`frontend/e2e/approval.spec.ts`).

### 변경
- 양방향 relation = **single_property + 샘플 링크 미러링** (이전 dual_property 폐기 — 반대편 relation 이름을 덮어써 그 측 rollup을 깨뜨렸음).
- 미사용 중복 채팅 UI(`MainLayout → ChatWindow` 체인) 제거.

### 알려진 한계 (정직 고지)
- AI 생성은 provider 가용성 의존. Gemini 키 쿼터 소진(429) 시 copilot/Groq 의존, 동시 실패 시 generic 폴백으로 graceful degradation(고지 포함).
- AI 샘플 날짜가 과거로 생성될 수 있어 날짜 수식이 음수/큰 값 가능(로직 정상).
- 단일 워커 권장. 48개 스킬 중 일부 라이브 미검증.
- **하드코딩 아님**: 정상 자연어 경로는 LLM이 전 구조를 자유 설계(`ai_dynamic`). 하드코딩은 (a) 전 provider 실패 시 비상 폴백, (b) 큐레이션 예제 갤러리(recipes)뿐.

---

## Docker Images
```bash
docker pull ghcr.io/jaylenai/notion_forge-backend:latest
docker pull ghcr.io/jaylenai/notion_forge-frontend:latest
```

## Quick Start
```bash
git clone https://github.com/JaylenAI/Notion_Forge
cd notionforge
cp .env.example .env
docker compose up -d
```
