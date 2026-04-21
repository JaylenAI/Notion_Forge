---
name: movie
description: Creates movie and drama watchlog templates with ratings, platform tracking, genre categorization, and poster gallery browsing.
---

# Movie (영화/드라마 기록)

Creates templates for logging movies and dramas with ratings, reviews, and visual poster galleries. Users track what they have watched, rate content, and build a personal watchlog across streaming platforms.

## Quick Start

1. **Identify viewing context**: What kind of content does the user watch and log?
2. **Design properties**: Title + genre + platform + rating + status + date + context fields
3. **Set layout**: Two-column (Quick Action sidebar 25% + main content 75%)
4. **Add gallery view**: Poster-based card display is essential for visual browsing
5. **Generate samples**: 5 realistic Korean/international titles with full metadata

## Template Structure

### Layout
Two-column: left 25% (Quick Action + Menu) / right 75% (content area)

### Block Order
1. callout: Cinematic welcome message (purple_background, 🎬)
2. empty paragraph (whitespace)
3. column_list:
   - left column (30%):
     - callout: "🎬 총 감상 작품" (pink_background)
     - callout: "⭐ 평균 평점" (pink_background)
   - right column (70%):
     - heading_2: Template title (purple)
     - callout: "나만의 영화 기록을 둘러보세요 👇" (purple_background)
4. divider
5. database_ref: Inline database here
6. empty paragraph (whitespace)
7. divider
8. toggle: "📖 사용 가이드" with numbered setup steps
9. toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Database Design

Required properties (always include):
- title: 제목
- select: 장르 (액션/드라마/코미디/SF/호러/로맨스/스릴러/다큐멘터리)
- select: 플랫폼 (넷플릭스/디즈니+/왓챠/티빙/쿠팡플레이/극장/웨이브)
- number: 평점 (1-5)
- status: 상태 (보고싶은/보는중/완료)
- date: 감상일

Context-dependent properties:
- select: 유형 (영화/드라마/애니/다큐)
- rich_text: 한줄평/리뷰
- checkbox: 추천 여부
- rich_text: 감독/출연진
- number: 러닝타임 (분)

### Views
- Required: gallery (포스터 갤러리 뷰)
- Optional: table (전체 감상 목록), board (상태별 칸반 보드)

### Sub-Pages
- 🎯 보고 싶은 리스트: Watchlist of upcoming movies and dramas
- ✍️ 감상 노트: Detailed reviews and memorable quotes

### Sample Data rules
Generate 5 items with REAL movie/drama titles popular in Korea.
Each item: unique icon, varied genres, different platforms, varied ratings and statuses.

## Content Adaptation Examples

**영화 감상록**: Properties → 감독(rich_text), 장르(select), 평점(number), 플랫폼(select), 한줄평(rich_text), 재관람(checkbox)
**드라마 기록**: Properties → 회차(number), 시즌(number), 장르(select), 진행률(number/%), 플랫폼(select), 완주여부(checkbox)
**애니메이션**: Properties → 스튜디오(select: 지브리/교토애니/본즈/매드하우스), 화수(number), 원작(select: 만화/소설/오리지널), 자막/더빙(select)
**다큐멘터리**: Properties → 주제(select: 자연/사회/역사/과학/음식), 제작국가(select), 러닝타임(number), 교훈(rich_text)
**극장 관람**: Properties → 상영관(select: IMAX/4DX/돌비/일반), 좌석(rich_text), 동행인(rich_text), 티켓가격(number), 팝콘(checkbox)
**시리즈 추적**: Properties → 시즌수(number), 현재시즌(number), 현재화(number), 다음방영일(date), 완결여부(checkbox)

## Formatting Rules

- Gallery view should be the DEFAULT view (poster-first visual browsing)
- Icon should be 🎬 or cinema-related (🎥🍿📺🎞️)
- Purple theme conveys cinematic, creative atmosphere
- Rating should be 1-5 scale (star-based)
- Platform options should reflect current Korean streaming landscape
- Sample data should include both Korean and international titles

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±2 weeks
- Examples: "🎬 파묘" (장르: 스릴러, 플랫폼: 극장, 평점: 5, 상태: 완료, 추천: true), "📺 눈물의 여왕" (장르: 로맨스, 플랫폼: 넷플릭스, 평점: 4, 상태: 보는중, 유형: 드라마), "🎥 듄: 파트 2" (장르: SF, 플랫폼: 극장, 평점: 5, 상태: 완료, 추천: true), "🍿 범죄도시 4" (장르: 액션, 플랫폼: 쿠팡플레이, 평점: 4, 상태: 완료, 추천: true), "📺 정신병동에도 아침이 와요" (장르: 드라마, 플랫폼: 넷플릭스, 평점: 5, 상태: 완료, 추천: true)
- Status values: spread across 보고싶은, 보는중, 완료
- Select values: use different genres and platforms

## Pro Design Guide

### Color Palette
- Primary: purple | Accent: pink | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 🎬 총 감상 작품 (callout, pink_background)
  - ⭐ 평균 평점 (callout, pink_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "오늘 뭐 볼까? 나만의 영화 기록을 시작해보세요 🎬" (purple_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with gallery view (기본), table view (상세)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "creative" (maps to themed Unsplash cover)
