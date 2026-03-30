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

## Formatting Rules

- Table view is PRIMARY (data-heavy content)
- Category sidebar helps navigation
- Filter-friendly property design
- Clean, structured layout

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±2 weeks
- Status values: spread across all statuses (시작 전, 진행 중, 완료)
- Select values: use different options for variety
- Number values: use realistic, varied numbers
- Checkbox: mix of true and false
