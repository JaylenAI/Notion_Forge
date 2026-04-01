---
name: collect
description: Creates collection/record templates for gathering items with card-based browsing. Wine, books, recipes, movies, archives, reviews.
---

# Collect (수집/기록)

Creates templates for collecting and recording items with visual card browsing. Ideal for personal collections, tasting notes, reading logs, and content archives.

## Quick Start

1. **Identify collection context**: What is the user collecting?
2. **Design properties**: Title + category + rating/checkbox + date + context-specific fields
3. **Set layout**: Two-column (Quick Action sidebar 25% + main content 75%)
4. **Add gallery view**: Card-based display is essential for collections
5. **Generate samples**: 5 realistic items with proper names (not generic)

## Template Structure

### Layout
Two-column: left 25% (Quick Action + Menu) / right 75% (content area)

### Block Order
1. callout: Welcome message (theme color, context icon)
2. divider
3. column_list:
   - left column:
     - heading_2: "Quick Action"
     - callout: "Add new record" (theme color, ✏️)
     - callout: "Write journal" (theme color, 📓)
     - divider
     - heading_2: "Menu"
     - link_to_page: sub-page 1
     - link_to_page: sub-page 2
   - right column:
     - heading_1: Template title (theme color)
     - callout: "Browse your collection below" (👇, theme color)
4. divider
5. database_ref: Inline database here
6. divider
7. toggle: Usage guide

### Database Design

Required properties (always include):
- title: Item name
- select: Category/type
- checkbox: Favorite/bookmark
- date: Record date

Context-dependent properties:
- number: Rating (1-5 or 1-10)
- rich_text: Notes, review, tasting notes
- url: Reference link
- select: Additional categorization (origin, author, etc.)

### Views
- Required: gallery (card-based visual browsing)
- Optional: calendar (date-based), table (detailed list)

### Sub-Pages
Generate 2 sub-pages matching context:
- Pattern: [Storage/Inventory] + [Journal/Notes]
- Examples: "Wine Cellar" + "Tasting Journal", "Reading List" + "Book Notes"

### Sample Data
Generate 5 items with REAL names (actual wine names, book titles, restaurant names).
Each item: unique icon, varied categories, different ratings.

## Content Adaptation Examples

**Wine**: Properties → grape, vintage, region, tasting notes, rating, price range
**Books**: Properties → author, genre, reading status, rating, started/finished date
**Recipes**: Properties → cuisine, difficulty, cook time, servings, ingredients count
**Restaurants**: Properties → location, cuisine type, price range, rating, last visited
**Movies**: Properties → director, genre, rating, watched date, platform
**Archives**: Properties → source type(article/video/podcast), tags, read status, URL
**Music/Vinyl**: Properties → artist, album, genre, format(vinyl/CD/digital), rating, purchase date
**Plants/Garden**: Properties → species, location(indoor/outdoor), watering schedule, last watered, health status
**Travel Souvenirs**: Properties → country, city, item type, purchase price, memory/story
**Coffee/Tea**: Properties → origin, roast level, brew method, flavor notes, rating

## Formatting Rules

- Gallery view should be the DEFAULT view (visual first)
- Icon should match context (🍷🍺📚🍳🎬🎵📦)
- Sub-pages should have relevant icons
- Callout text should be warm and inviting

## Color Theme Guide

Recommended color combinations by context:
- Wine/Spirits: red (warm, rich) — callout: red_background, headings: red
- Books/Reading: blue (calm, intellectual) — callout: blue_background, headings: blue
- Recipes/Cooking: orange (appetizing, warm) — callout: orange_background, headings: orange
- Restaurants/Cafe: yellow (friendly, inviting) — callout: yellow_background, headings: yellow
- Movies/TV: purple (cinematic, creative) — callout: purple_background, headings: purple
- Music/Vinyl: pink (expressive, artistic) — callout: pink_background, headings: pink
- Archives/Clippings: gray (neutral, organized) — callout: gray_background, headings: gray
- Plants/Garden: green (natural, living) — callout: green_background, headings: green
- Travel Souvenirs: orange (adventurous, energetic) — callout: orange_background, headings: orange
- Default: gray (neutral, clean)

## Complexity Levels

### Simple (5-8 blocks): Quick collection
callout → heading_1 → database_ref → toggle(usage tip)

### Medium (10-15 blocks): Standard collection with sidebar
callout → divider → column_list(quick action sidebar + main content) → database_ref → divider → toggle(usage) → toggle(FAQ)

### Complex (20-30 blocks): Full collection system
callout → quote(collection motto) → divider → column_list(quick action + menu sidebar + main content area) → heading_1 → database_ref → divider → heading_2(categories overview) → bulleted_list(category breakdown) → heading_2(rating guide) → numbered_list(criteria) → toggle(FAQ x3) → toggle(advanced search tips) → toggle(import/export guide)

## Cross-Skill Combinations

- collect + track: "독서하면서 독서 습관도 기록" — Use collect for book collection/reviews + track for daily reading minutes log
- collect + organize: "레시피 수집 + 식재료 정리" — Use collect for recipe gallery + organize for pantry/ingredient inventory
- collect + plan: "여행지 수집 + 여행 계획" — Use collect for destination/restaurant collection + plan for trip itinerary & checklist
- collect + hub: "취미 아카이브 허브" — Use hub as central hobby dashboard + collect DBs for each hobby (wine, books, movies)
- collect + guide: "와인 입문 가이드 + 테이스팅 기록" — Use guide for wine education doc + collect for personal tasting notes collection

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±2 weeks
- Status values: spread across all statuses (시작 전, 진행 중, 완료)
- Select values: use different options for variety
- Number values: use realistic, varied numbers
- Checkbox: mix of true and false

## Pro Design Guide

### Color Palette
- Primary: purple | Accent: pink | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 📚 총 컬렉션 (callout, pink_background)
  - ⭐ 즐겨찾기 (callout, pink_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "나만의 컬렉션을 만들어보세요! 수집의 즐거움이 여기에 ✨" (purple_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with gallery view (기본), table view (상세)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "creative" (maps to themed Unsplash cover)
