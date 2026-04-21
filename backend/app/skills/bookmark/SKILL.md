---
name: bookmark
description: Creates bookmark and link management templates for web resource curation, category tagging, and reading list tracking. Table-driven with gallery and list views.
---

# Bookmark (북마크/링크 정리)

Creates templates for web bookmark management including link curation, category organization, tag-based filtering, and reading list tracking.

## Quick Start

1. **Identify bookmark context**: What does the user collect? (dev resources, design inspiration, articles, tools, references)
2. **Design properties**: Always include url + select(category) + multi_select(tags). Add context-specific fields.
3. **Set layout**: Two-column (left 25% category summary / right 75% bookmark DB)
4. **Add table view**: Essential for searchable, filterable link management
5. **Generate samples**: 5 bookmarks across different categories with realistic URLs

## Template Structure

### Layout
Two-column (left 25% category stats / right 75% bookmark database)

### Block Order
1. callout: Bookmark collection intro message (theme color, context icon)
2. column_list:
   - Column 1 (25%): Total links callout + recently added callout
   - Column 2 (75%): Main bookmark content area
3. divider
4. heading_1: Main title (theme color)
5. database_ref: Inline database here
6. toggle: "북마크 정리 규칙" with tagging conventions and category guidelines

### Database Design

Required properties (always include):
- title: Page/resource title
- url: Link URL
- select: Category (개발/디자인/마케팅/참고자료/도구/학습)
- multi_select: Tags

Context-dependent properties (AI decides):
- rich_text: Description/summary
- date: Date added
- checkbox: Read/reviewed
- select: Priority (필독/추천/참고/나중에)
- select: Type (아티클/영상/도구/레포/문서/강의)
- rich_text: Key takeaway
- number: Rating (1-5)
- rich_text: Source/author

### Views
- Required: table (PRIMARY - searchable list with all metadata)
- Optional: gallery (visual card preview with descriptions)
- Optional: list (compact quick-scan view)
- Optional: board (grouped by category)

### Sub-Pages
- "읽기 목록" (Reading List): Curated must-read articles and resources queue
- "추천 도구 모음" (Tool Collection): Best tools and services organized by purpose

### Sample Data
Generate 5 bookmarks across different categories with realistic Korean tech/design data.
Each item needs: relevant icon, URL, category, tags, and description.

## Content Adaptation Examples

**Dev Resources**: Properties → language(multi_select), framework, difficulty(초급/중급/고급), github stars, last updated
**Design Inspiration**: Properties → design type(UI/UX/그래픽/브랜딩), tool used, style(미니멀/볼드/일러스트), platform(Dribbble/Behance)
**Article Curation**: Properties → author, publication, read time(number), topic, key insight(rich_text), read status
**Tool Directory**: Properties → pricing(무료/프리미엄/유료), platform(웹/앱/데스크톱), use case, alternative tools
**Learning Resources**: Properties → course platform, duration, level, certification(checkbox), progress%, instructor
**Research Papers**: Properties → authors, journal, year, citation count, abstract(rich_text), field

## Formatting Rules

- Callout icon should match context (🔗 general, 💻 dev, 🎨 design, 📰 article, 🔧 tool)
- Table view is the PRIMARY view (search and filter are key for bookmarks)
- Keep properties under 9 (bookmarks need metadata but should be quick to add)
- Tags should be free-form multi_select for flexible categorization
- Quick stats callout should show key metrics (total bookmarks, unread count, this week added)

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±4 weeks
- Category values: spread across options (개발, 디자인, 마케팅, 참고자료, 도구, 학습)
- Tags: realistic Korean tech tags (React, TypeScript, UI디자인, SEO, 생산성, API, Figma)
- URLs: realistic resource URLs (github.com, medium.com, figma.com, notion.so, youtube.com)
- Descriptions: concise Korean summaries (React 18 새로운 기능 정리, Figma 플러그인 추천 모음, SEO 최적화 가이드)
- Titles: realistic Korean resource titles (프론트엔드 로드맵 2026, 디자인 시스템 구축 가이드, 무료 아이콘 모음 사이트)
- Priority: mix of 필독, 추천, 참고, 나중에

## Pro Design Guide

### Color Palette
- Primary: blue | Accent: gray | Secondary: default
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 🔗 전체 북마크 (callout, gray_background)
  - 📖 읽지 않은 항목 (callout, gray_background)
  - 📌 이번 주 추가 (callout, gray_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "유용한 링크를 한곳에! 필요할 때 바로 찾아보세요 🔗" (blue_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with table view (기본, 전체 목록), gallery view (카드), board view (카테고리별)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "tech" (maps to themed Unsplash cover)
