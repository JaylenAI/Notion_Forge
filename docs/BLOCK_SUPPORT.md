# Notion 블록/기능 지원 현황 (Block Support Status)

> 최종 업데이트: 2026-03-27
> 실제 Notion 생성 테스트 완료

---

## Phase A: 기본 블록 — ✅ 전부 완료

| # | 기능 | 블록 타입 | 상태 | 테스트 |
|---|------|----------|------|--------|
| A1 | heading_1/2/3 | `heading_1/2/3` | ✅ 완료 | ✅ 확인 |
| A2 | heading_4 | `heading_4` | ✅ 완료 | - |
| A3 | paragraph | `paragraph` | ✅ 완료 | ✅ 확인 |
| A4 | callout | `callout` | ✅ 완료 | ✅ 확인 |
| A5 | toggle | `toggle` | ✅ 완료 | ✅ 확인 |
| A6 | to_do | `to_do` | ✅ 완료 | ✅ 확인 |
| A7 | divider | `divider` | ✅ 완료 | ✅ 확인 |
| A8 | bulleted_list | `bulleted_list_item` | ✅ 완료 | ✅ 확인 |
| A9 | numbered_list | `numbered_list_item` | ✅ 완료 | ✅ 확인 |
| A10 | **quote (인용)** | `quote` | ✅ 완료 | ✅ 확인 |
| A11 | **table (정적 테이블)** | `table` + `table_row` | ✅ 완료 | ✅ 확인 |
| A12 | link_to_page | `link_to_page` | ✅ 완료 | ✅ 확인 |

## Phase B: 인라인 서식 — ✅ 전부 완료

| # | 기능 | 구현 방법 | 상태 | 테스트 |
|---|------|----------|------|--------|
| B1 | bold (굵게) | `annotations.bold` | ✅ 완료 | ✅ 확인 |
| B2 | **italic (기울임)** | `annotations.italic` | ✅ 완료 | ✅ 확인 |
| B3 | **underline (밑줄)** | `annotations.underline` | ✅ 완료 | ✅ 확인 |
| B4 | **strikethrough (취소선)** | `annotations.strikethrough` | ✅ 완료 | ✅ 확인 |
| B5 | **inline code** | `annotations.code` | ✅ 완료 | ✅ 확인 |
| B6 | **link (링크)** | `text.link.url` | ✅ 완료 | ✅ 확인 |
| B7 | text color (10색) | `annotations.color` | ✅ 완료 | ✅ 확인 |
| B8 | background color (10색) | `_background` | ✅ 완료 | ✅ 확인 |
| B9 | mention (page) | `mention.page` | ✅ 완료 | - |
| B10 | mention (date) | `mention.date` | ✅ 완료 | - |
| B11 | mention (user) | `mention.user` | ✅ 완료 | - |
| B12 | **inline equation** | rich_text `equation` | ✅ 완료 | ✅ 확인 |

## Phase C: 미디어 — ✅ 전부 완료

| # | 기능 | 블록 타입 | 상태 | 테스트 |
|---|------|----------|------|--------|
| C1 | **code block** | `code` (60+ 언어) | ✅ 완료 | ✅ 확인 |
| C2 | image | `image` | ✅ 완료 | ✅ 확인 |
| C3 | bookmark | `bookmark` | ✅ 완료 | ✅ 확인 |
| C4 | **video** | `video` | ✅ 완료 | - |
| C5 | **audio** | `audio` | ✅ 완료 | - |
| C6 | **file** | `file` | ✅ 완료 | - |
| C7 | **pdf** | `pdf` | ✅ 완료 | - |

## Phase D: 고급 블록 — ✅ 전부 완료

| # | 기능 | 블록 타입 | 상태 | 테스트 |
|---|------|----------|------|--------|
| D1 | table_of_contents | `table_of_contents` | ✅ 완료 | ✅ 확인 |
| D2 | **breadcrumb** | `breadcrumb` | ✅ 완료 | ✅ 확인 |
| D3 | **equation block** | `equation` | ✅ 완료 | ✅ 확인 |
| D4 | **synced_block** | `synced_block` | ✅ 완료 | - |
| D5 | column_list (2~5단) | `column_list` | ✅ 완료 | ✅ 확인 |
| D6 | **toggle heading** | `is_toggleable: true` | ✅ 완료 | - |
| D7 | tab | `tab` | ✅ 완료 | - |

## Phase E: 임베드 — ✅ 전부 완료

| # | 기능 | 구현 | 상태 |
|---|------|------|------|
| E1 | **Generic embed** | `embed` + URL | ✅ 완료 |
| E2 | Google Drive | `embed` | ✅ 완료 |
| E3 | Google Maps | `embed` | ✅ 완료 |
| E4 | Figma | `embed` | ✅ 완료 |
| E5 | GitHub Gist | `embed` | ✅ 완료 |
| E6 | Tweet/X | `embed` | ✅ 완료 |
| E7 | Loom | `embed` | ✅ 완료 |
| E8 | Miro | `embed` | ✅ 완료 |
| E9 | Abstract | `embed` | ✅ 완료 |
| E10 | CodePen | `embed` | ✅ 완료 |
| E11 | Whimsical | `embed` | ✅ 완료 |
| E12 | PDF embed | `pdf` | ✅ 완료 |

## DB 뷰 — ✅ 10개 전부 완료

| 뷰 | 상태 | 테스트 |
|----|------|--------|
| table / board / calendar / timeline / gallery / list / chart / form / map / dashboard | ✅ | ✅ 10개 전부 확인 |

---

## 최종 점수

| 카테고리 | 전체 | 구현 | 비율 |
|----------|------|------|------|
| 기본 블록 | 12 | **12** | 100% |
| 인라인 서식 | 12 | **12** | 100% |
| 미디어 | 7 | **7** | 100% |
| 고급 블록 | 7 | **7** | 100% |
| 임베드 | 12 | **12** | 100% |
| DB 뷰 | 10 | **10** | 100% |
| **합계** | **60** | **60** | **100%** |

## Phase F: Notion API 확장 기능 -- 2026-03-27 추가

| # | 기능 | 구현 위치 | 상태 |
|---|------|----------|------|
| F1 | Search API (워크스페이스 검색) | `client.py` `search()` | ✅ 완료 |
| F2 | Users API (목록/조회) | `client.py` `list_users()`, `get_user()` | ✅ 완료 |
| F3 | Comments API (추가/조회) | `client.py` `add_comment()`, `get_comments()` | ✅ 완료 |
| F4 | Page archive/restore | `client.py` `archive_page()`, `restore_page()` | ✅ 완료 |
| F5 | Page/DB lock | `client.py` `lock_page()`, `lock_database()` | ✅ 완료 |
| F6 | Markdown API (생성/조회) | `client.py` `create_page_markdown()`, `get_page_markdown()` | ✅ 완료 |
| F7 | Custom Emoji API | `client.py` `list_custom_emojis()` | ✅ 완료 |
| F8 | DB mention (인라인) | `block_builder.py` `rich_text_mention_database()` | ✅ 완료 |
| F9 | Template mention (@today/@now/@me) | `block_builder.py` `rich_text_template_mention()` | ✅ 완료 |
| F10 | Icon helpers (emoji/external/native/custom) | `block_builder.py` `icon_*()` | ✅ 완료 |
| F11 | DB property: relation/formula/rollup | `block_builder.py` `build_database_properties()` | ✅ 완료 |
| F12 | DB property: auto-generated types | `block_builder.py` `build_database_properties()` | ✅ 완료 |
| F13 | DB item: people/files/phone/relation | `add_database_items.py` `_format_value()` | ✅ 완료 |
| F14 | Router: search/comment/lock/archive | `template.py` endpoints | ✅ 완료 |

## 최종 점수 (업데이트)

| 카테고리 | 전체 | 구현 | 비율 |
|----------|------|------|------|
| 기본 블록 | 12 | **12** | 100% |
| 인라인 서식 | 12 | **12** | 100% |
| 미디어 | 7 | **7** | 100% |
| 고급 블록 | 7 | **7** | 100% |
| 임베드 | 12 | **12** | 100% |
| DB 뷰 | 10 | **10** | 100% |
| API 확장 기능 | 14 | **14** | 100% |
| **합계** | **74** | **74** | **100%** |

---

## 절대 불가능 (API 미지원, 5개)

| 기능 | 이유 | 대안 |
|------|------|------|
| Button 블록 | `unsupported` | 콜아웃으로 대체 |
| AI 블록/요약 | API 미노출 | Groq/Claude AI로 대체 |
| Link Preview | 읽기만 | bookmark 사용 |
| 전체 너비/폰트 | API 미노출 | 안내 메시지 |
| Template Button | deprecated | DB "새로 만들기" |
