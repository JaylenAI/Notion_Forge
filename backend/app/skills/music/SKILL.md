---
name: music
description: Creates music library and playlist templates with mood tagging, genre categorization, artist tracking, and album cover gallery browsing.
---

# Music (음악/플레이리스트)

Creates templates for organizing a personal music library with mood-based playlists, genre categorization, and album art galleries. Users curate their favorite tracks, discover listening patterns, and build themed playlists.

## Quick Start

1. **Identify music context**: What kind of music curation does the user want?
2. **Design properties**: Title + artist + genre + mood + rating + context fields
3. **Set layout**: Two-column (Quick Action sidebar 25% + main content 75%)
4. **Add gallery view**: Album cover card display is essential for visual browsing
5. **Generate samples**: 5 realistic Korean/international track titles with full metadata

## Template Structure

### Layout
Two-column: left 25% (Quick Action + Menu) / right 75% (content area)

### Block Order
1. callout: Music-themed welcome message (pink_background, 🎵)
2. empty paragraph (whitespace)
3. column_list:
   - left column (30%):
     - callout: "🎵 총 수록곡" (purple_background)
     - callout: "❤️ 즐겨찾기" (purple_background)
   - right column (70%):
     - heading_2: Template title (pink)
     - callout: "나만의 음악 라이브러리를 둘러보세요 👇" (pink_background)
4. divider
5. database_ref: Inline database here
6. empty paragraph (whitespace)
7. divider
8. toggle: "📖 사용 가이드" with numbered setup steps
9. toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Database Design

Required properties (always include):
- title: 곡명
- rich_text: 아티스트
- select: 장르 (K-POP/팝/힙합/R&B/인디/클래식/재즈/OST/발라드)
- multi_select: 분위기 (신나는/잔잔한/우울한/에너지/로맨틱/집중/새벽감성)
- number: 평점 (1-5)
- date: 추가일

Context-dependent properties:
- rich_text: 앨범명
- checkbox: 즐겨찾기
- url: 음원 링크 (스포티파이/멜론/유튜브)
- select: 플랫폼 (멜론/스포티파이/애플뮤직/유튜브뮤직)
- rich_text: 메모/가사 인용

### Views
- Required: gallery (앨범 커버 갤러리)
- Optional: table (전체 곡 목록 및 필터링), board (장르별 그룹핑)

### Sub-Pages
- 🎧 플레이리스트 모음: Curated playlists by mood/occasion
- 🎤 아티스트 노트: Favorite artists and concert memories

### Sample Data rules
Generate 5 items with REAL song/artist names popular in Korea.
Each item: unique icon, varied genres, different moods, varied ratings.

## Content Adaptation Examples

**K-POP 컬렉션**: Properties → 그룹/솔로(select), 앨범(rich_text), 타이틀곡(checkbox), 발매일(date), 뮤비조회수(number), 팬덤(rich_text)
**플레이리스트 큐레이션**: Properties → 플레이리스트명(select: 출근길/운동/공부/드라이브/취침전), 분위기(multi_select), BPM(number), 재생시간(rich_text)
**바이닐/LP 수집**: Properties → 포맷(select: LP/CD/카세트/디지털), 구매처(rich_text), 구매가격(number), 한정판(checkbox), 컨디션(select: 민트/양호/보통)
**콘서트/공연 기록**: Properties → 공연장(rich_text), 날짜(date), 좌석(rich_text), 티켓가격(number), 동행인(rich_text), 만족도(number)
**작업용 BGM**: Properties → 용도(select: 코딩/글쓰기/디자인/회의), 재생시간(rich_text), 가사유무(select: 가사없음/영어/한국어), 집중도(select: 상/중/하)
**악기 연습곡**: Properties → 악기(select: 피아노/기타/드럼/우쿨렐레), 난이도(select), 연습시간(number/분), 완성도(select: 연습중/거의완성/마스터)

## Formatting Rules

- Gallery view should be the DEFAULT view (album art visual browsing)
- Icon should be 🎵 or music-related (🎶🎧🎤🎸)
- Pink theme conveys artistic expression and emotional connection
- Mood tags should be colorful multi_select options
- Sample data should include both Korean and international artists
- Genre options should reflect Korean music consumption patterns

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±2 weeks
- Examples: "🎵 Supernova" (아티스트: aespa, 장르: K-POP, 분위기: [신나는, 에너지], 평점: 5, 즐겨찾기: true), "🎶 HAPPY" (아티스트: Day6, 장르: 인디, 분위기: [신나는, 에너지], 평점: 5, 즐겨찾기: true), "🎧 Die With A Smile" (아티스트: Lady Gaga & Bruno Mars, 장르: 팝, 분위기: [잔잔한, 로맨틱], 평점: 4, 즐겨찾기: true), "🎤 해요 (2024)" (아티스트: 이무진, 장르: 발라드, 분위기: [잔잔한, 새벽감성], 평점: 4, 즐겨찾기: false), "🎸 Drama" (아티스트: aespa, 장르: K-POP, 분위기: [신나는], 평점: 4, 즐겨찾기: false)
- Multi_select values: varied mood combinations
- Select values: spread across all genres

## Pro Design Guide

### Color Palette
- Primary: pink | Accent: purple | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 🎵 총 수록곡 (callout, purple_background)
  - ❤️ 즐겨찾기 (callout, purple_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "음악이 있는 하루, 나만의 플레이리스트를 만들어보세요 🎵" (pink_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with gallery view (기본), table view (상세)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "creative" (maps to themed Unsplash cover)
