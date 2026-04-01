---
name: organize
description: Creates organization templates for structuring information. Bookmarks, contacts, budgets, inventory, catalogs.
---

# Organize (정리/구조화)

Creates templates for organizing and categorizing information with strong filtering and sorting.

## Quick Start

1. **Identify what's being organized**: Bookmarks, contacts, finances, etc.
2. **Design properties**: Title + category + key metadata fields
3. **Set layout**: Two-column (category sidebar + main table)
4. **Add table view**: Structured data needs table with filters
5. **Generate samples**: 5 well-categorized items

## Template Structure

### Layout
Two-column: left 30% (category list) / right 70% (content + DB)

### Block Order
1. column_list:
   - left column:
     - heading_2: "Categories" (theme color)
     - bulleted_list: Category 1
     - bulleted_list: Category 2
     - bulleted_list: Category 3
     - (etc.)
   - right column:
     - callout: Guide message (theme color)
     - divider
     - heading_1: Title (theme color)
     - callout: "Browse below" (👇)
2. divider
3. database_ref: Inline database here

### Database Design

Required properties:
- title: Item name
- select: Primary category
- url or email or phone: Key contact/link field

Context-dependent:
- rich_text: Notes, description
- number: Amount, quantity, price
- checkbox: Active/favorite
- date: Added date, expiry

### Views
- Required: table (structured, filterable)
- Optional: gallery (if visual), list (simple)

### Sub-Pages
Usually none.

### Sample Data
Generate 5 items spread across different categories.

## Content Adaptation Examples

**Bookmarks**: Properties → URL, category, description, favorite
**Contacts**: Properties → company, email, phone, role, last contacted
**Budget**: Properties → category(food/housing/transport), amount, month, type(income/expense)
**Inventory**: Properties → category, quantity, location, reorder level, cost
**Catalog**: Properties → category, price, availability, SKU
**Subscriptions**: Properties → service name, cost/month, billing date, category(streaming/software/news), auto-renew
**Passwords/Accounts**: Properties → service, username, email, category, last updated, 2FA enabled
**Wardrobe/Closet**: Properties → type(top/bottom/shoes/accessory), color, season, brand, last worn
**Digital Files**: Properties → file name, type(doc/image/video), folder, size, tags, date added
**Gift Ideas**: Properties → recipient, occasion, item, price range, purchased status, notes

## Formatting Rules

- Table view is PRIMARY (data-heavy content)
- Category sidebar helps navigation
- Filter-friendly property design
- Clean, structured layout

## Color Theme Guide

Recommended color combinations by context:
- Bookmarks/Links: blue (web, digital) — callout: blue_background, headings: blue
- Contacts/CRM: purple (people, relationships) — callout: purple_background, headings: purple
- Budget/Finance: green (money, growth) — callout: green_background, headings: green
- Inventory/Stock: yellow (warehouse, attention) — callout: yellow_background, headings: yellow
- Catalog/Products: orange (commercial, attractive) — callout: orange_background, headings: orange
- Files/Documents: gray (formal, structured) — callout: gray_background, headings: gray
- Subscriptions: red (recurring, attention) — callout: red_background, headings: red
- Passwords/Accounts: red (security, caution) — callout: red_background, headings: red
- Default: gray (neutral, clean)

## Complexity Levels

### Simple (5-8 blocks): Quick organizer
callout → heading_1 → database_ref → toggle(usage tip)

### Medium (10-15 blocks): Standard organizer with sidebar
callout → divider → column_list(category sidebar + main content) → database_ref → divider → toggle(filter guide) → toggle(FAQ)

### Complex (20-30 blocks): Full organization system
callout → quote(organizing principle) → divider → column_list(category tree sidebar + main content with summary stats) → heading_1 → database_ref → divider → heading_2(category guide) → bulleted_list(category descriptions) → heading_2(maintenance) → to_do(weekly cleanup checklist) → toggle(naming conventions) → toggle(archiving policy) → toggle(FAQ x3) → toggle(import/export tips)

## Cross-Skill Combinations

- organize + collect: "식재료 정리 + 레시피 수집" — Use organize for pantry/ingredient inventory + collect for recipe collection gallery
- organize + manage: "고객 정리 + 영업 관리" — Use organize for contact directory + manage for sales pipeline board
- organize + plan: "짐 목록 정리 + 이사 계획" — Use organize for belongings inventory + plan for moving checklist & timeline
- organize + track: "가계부 정리 + 지출 추적" — Use organize for budget categories & accounts + track for daily spending log
- organize + hub: "리소스 센터" — Use hub as resource home with navigation + organize for each resource type (links, files, contacts)

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±2 weeks
- Status values: spread across all statuses (시작 전, 진행 중, 완료)
- Select values: use different options for variety
- Number values: use realistic, varied numbers
- Checkbox: mix of true and false
