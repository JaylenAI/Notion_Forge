---
name: cafe
description: Creates cafe and restaurant discovery templates for visit logs, ratings, menus, and atmosphere tracking. Gallery-driven with map-style and calendar views.
---

# Cafe (카페/맛집 기록)

Creates templates for cafe exploration and restaurant discovery including visit logging, atmosphere ratings, menu notes, and location tracking.

## Quick Start

1. **Identify cafe context**: What does the user want to record? (cafe visits, restaurant reviews, dessert spots, brunch places)
2. **Design properties**: Always include select(atmosphere) + number(rating) + date(visit). Add context-specific fields.
3. **Set layout**: Two-column (left 25% favorites summary / right 75% gallery DB)
4. **Add gallery view**: Essential for visual cafe/food photo browsing
5. **Generate samples**: 5 cafes with diverse atmospheres, locations, and ratings

## Template Structure

### Layout
Two-column (left 25% favorites & stats / right 75% cafe gallery database)

### Block Order
1. callout: Cafe exploration intro message (theme color, context icon)
2. column_list:
   - Column 1 (25%): Best picks callout + monthly visit count callout
   - Column 2 (75%): Main gallery content area
3. divider
4. heading_1: Main title (theme color)
5. database_ref: Inline database here
6. toggle: "카페 탐방 체크리스트" with wifi, parking, pet-friendly tips

### Database Design

Required properties (always include):
- title: Cafe/restaurant name
- select: Atmosphere (아늑한/모던/레트로/조용한/활기찬/루프탑)
- number: Rating (1-5 scale)
- date: Visit date

Context-dependent properties (AI decides):
- rich_text: Location/address
- rich_text: Signature menu
- number: Price range (average per person)
- select: Category (카페/브런치/디저트/베이커리/맛집)
- multi_select: Features (와이파이/콘센트/주차/펫프렌들리/노키즈존)
- checkbox: Revisit wanted
- url: Instagram or map link
- rich_text: Notes/review

### Views
- Required: gallery (PRIMARY - visual cafe photo cards)
- Optional: table (all details with filtering)
- Optional: calendar (visit history timeline)

### Sub-Pages
- "가고 싶은 카페 리스트" (Wishlist): Curated list of places to visit next
- "베스트 메뉴 모음" (Best Menu Collection): Top dishes and drinks from visited places

### Sample Data
Generate 5 cafes with diverse atmospheres and realistic Korean cafe data.
Each item needs: relevant icon, atmosphere tag, rating, signature menu, and visit date.

## Content Adaptation Examples

**Cafe Explorer**: Properties → atmosphere, wifi quality(select), signature drink, seating(indoor/outdoor/terrace), noise level
**Restaurant Review**: Properties → cuisine type(한식/양식/일식/중식), price range, portion size, wait time, reservation needed
**Dessert Hunter**: Properties → dessert type, sweetness level(1-5), portion, instagram-worthy(checkbox), best item
**Brunch Spots**: Properties → brunch menu, coffee quality(1-5), ambiance, weekend wait time, set menu price
**Bakery Log**: Properties → bread type, freshness, baking time, specialty item, takeout available

## Formatting Rules

- Callout icon should match context (☕ cafe, 🍰 dessert, 🍽️ restaurant, 🥐 bakery)
- Gallery view is the PRIMARY view (visual discovery is key for cafe/food)
- Keep properties under 9 (focused on atmosphere and experience)
- Rating should use number format with 0.5 increments (1-5 scale)
- Quick stats callout should show key metrics (total visits, average rating, this month)

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic visit dates within ±4 weeks
- Atmosphere values: spread across options (아늑한, 모던, 레트로, 조용한, 활기찬)
- Rating values: varied realistic scores (3.5, 4.0, 4.5, 5.0, 3.0)
- Price range: realistic Korean cafe prices (5,000원, 7,500원, 12,000원, 15,000원)
- Location: realistic Seoul/Korean neighborhoods (연남동, 성수동, 한남동, 익선동, 망원동)
- Menu items: realistic Korean cafe menus (아인슈페너, 크로플, 당근케이크, 플랫화이트, 바스크치즈케이크)
- Cafe names: realistic Korean cafe names (어니언, 프릳츠, 블루보틀, 카페공명, 밀도)

## Pro Design Guide

### Color Palette
- Primary: brown | Accent: orange | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - ☕ 총 방문 카페 (callout, orange_background)
  - ⭐ 평균 평점 (callout, orange_background)
  - 📍 이번 달 탐방 (callout, orange_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "나만의 카페 지도를 만들어보세요! 한 잔의 여유와 함께 ☕" (brown_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with gallery view (기본, 카페 갤러리), table view (상세), calendar view (방문 기록)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "food" (maps to themed Unsplash cover)
