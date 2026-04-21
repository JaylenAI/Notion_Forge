---
name: reading
description: Creates reading log and book collection templates with rating, status tracking, gallery browsing, and reading goal management.
---

# Reading (독서 기록)

Creates templates for logging books with ratings, reading status, and personal reviews. Ideal for building a personal library, tracking reading goals, and discovering patterns in reading habits.

## Quick Start

1. **Identify reading context**: What kind of reading does the user track?
2. **Design properties**: Title + author + genre + status + rating + date + context fields
3. **Set layout**: Two-column (sidebar 25% + main content 75%)
4. **Add gallery view**: Card-based book cover display is essential
5. **Generate samples**: 5 realistic Korean/translated book titles with full metadata

## Template Structure

### Layout
Two-column: left 25% (Quick Action + Menu) / right 75% (content area)

### Block Order
1. callout: Reading encouragement message (blue_background, 📚)
2. empty paragraph (whitespace)
3. column_list:
   - left column (30%):
     - callout: "📖 올해 읽은 책" (green_background)
     - callout: "⭐ 평균 평점" (green_background)
   - right column (70%):
     - heading_2: Template title (blue)
     - callout: "책장을 둘러보세요 👇" (blue_background)
4. divider
5. database_ref: Inline database here
6. empty paragraph (whitespace)
7. divider
8. toggle: "📖 사용 가이드" with numbered setup steps
9. toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Database Design

Required properties (always include):
- title: 책 제목
- rich_text: 저자
- select: 장르 (소설/자기계발/기술/에세이/역사/과학/경제/시)
- status: 상태 (읽기 전/읽는 중/완독)
- number: 평점 (1-5)
- date: 시작일

Context-dependent properties:
- date: 완독일
- rich_text: 한줄평/서평
- number: 페이지수
- checkbox: 추천 여부
- select: 형태 (종이책/전자책/오디오북)

### Views
- Required: gallery (책 표지 갤러리 뷰)
- Optional: table (전체 목록 및 필터링), board (상태별 칸반)

### Sub-Pages
- 📋 읽고 싶은 책: Wishlist of books to read next
- ✍️ 독서 노트: Detailed notes and quotes from books

### Sample Data rules
Generate 5 items with REAL Korean book titles or well-known translated titles.
Each item: unique icon, varied genres, different reading statuses, varied ratings.

## Content Adaptation Examples

**일반 독서**: Properties → 저자(rich_text), 장르(select), 상태(status), 평점(number), 시작일/완독일(date), 한줄평(rich_text)
**학술 독서**: Properties → 분야(select: 논문/교재/레퍼런스), 중요도(select: 상/중/하), 핵심내용(rich_text), 인용횟수(number)
**독서 모임**: Properties → 모임날짜(date), 발제자(rich_text), 토론주제(rich_text), 참석여부(checkbox), 다음책(rich_text)
**어린이 독서**: Properties → 권장연령(select), 읽어준사람(select: 엄마/아빠/혼자), 반응(select: 좋아함/보통/관심없음), 재독횟수(number)
**오디오북**: Properties → 재생시간(number/hrs), 내레이터(rich_text), 플랫폼(select: 밀리/윌라/교보), 배속(select: 1x/1.5x/2x)
**전자책 구독**: Properties → 플랫폼(select), 월구독료(number), 이달읽은권수(number), 하이라이트수(number)

## Formatting Rules

- Gallery view should be the DEFAULT view (visual book browsing)
- Icon should be 📚 or book-related (📖📕✍️)
- Blue theme conveys calm, intellectual atmosphere
- Sub-pages should have relevant icons
- Callout text should be warm and encouraging for reading habits
- Rating should be 1-5 scale (star-based)

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±2 weeks
- Examples: "📕 아몬드" (저자: 손원평, 장르: 소설, 상태: 완독, 평점: 5, 추천: true), "📗 원씽" (저자: 게리 켈러, 장르: 자기계발, 상태: 읽는 중, 평점: 4, 추천: true), "📘 클린 코드" (저자: 로버트 마틴, 장르: 기술, 상태: 읽는 중, 평점: 4, 추천: true), "📙 나미야 잡화점의 기적" (저자: 히가시노 게이고, 장르: 소설, 상태: 완독, 평점: 5, 추천: true), "📓 역사의 쓸모" (저자: 최태성, 장르: 역사, 상태: 읽기 전, 평점: 0, 추천: false)
- Status values: spread across 읽기 전, 읽는 중, 완독
- Select values: use different genres for variety

## Pro Design Guide

### Color Palette
- Primary: blue | Accent: green | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 📖 올해 읽은 책 (callout, green_background)
  - ⭐ 평균 평점 (callout, green_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "한 권의 책이 인생을 바꿉니다. 나만의 서재를 채워보세요 📚" (blue_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with gallery view (기본), table view (상세)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "study" (maps to themed Unsplash cover)
