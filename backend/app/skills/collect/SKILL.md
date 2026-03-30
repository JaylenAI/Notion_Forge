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

## Formatting Rules

- Gallery view should be the DEFAULT view (visual first)
- Icon should match context (🍷🍺📚🍳🎬🎵📦)
- Sub-pages should have relevant icons
- Callout text should be warm and inviting

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±2 weeks
- Status values: spread across all statuses (시작 전, 진행 중, 완료)
- Select values: use different options for variety
- Number values: use realistic, varied numbers
- Checkbox: mix of true and false
