---
name: inventory
description: Creates inventory and asset management templates for item tracking, stock levels, location mapping, and purchase history. Table-driven with board and gallery views.
---

# Inventory (재고/물품 관리)

Creates templates for inventory and asset management including stock tracking, location organization, purchase history, and reorder alerts.

## Quick Start

1. **Identify inventory context**: What does the user manage? (office supplies, equipment, personal items, warehouse stock)
2. **Design properties**: Always include number(quantity) + select(category) + rich_text(location). Add context-specific fields.
3. **Set layout**: Two-column (left 25% stock summary / right 75% inventory DB)
4. **Add table view**: Essential for quantity-based inventory scanning
5. **Generate samples**: 5 items across different categories with realistic stock data

## Template Structure

### Layout
Two-column (left 25% stock overview / right 75% inventory database)

### Block Order
1. callout: Inventory management intro message (theme color, context icon)
2. column_list:
   - Column 1 (25%): Total items callout + low stock alert callout
   - Column 2 (75%): Main inventory content area
3. divider
4. heading_1: Main title (theme color)
5. database_ref: Inline database here
6. toggle: "재고 관리 규칙" with reorder policies and categorization guide

### Database Design

Required properties (always include):
- title: Item name
- number: Quantity in stock
- select: Category (전자기기/사무용품/가구/소모품/장비/기타)
- rich_text: Storage location

Context-dependent properties (AI decides):
- number: Unit price
- number: Total value (price x quantity)
- date: Purchase date
- date: Last checked date
- select: Condition (신품/양호/보통/수리필요/폐기예정)
- select: Priority (필수/일반/여유)
- number: Minimum stock level (reorder point)
- rich_text: Supplier/vendor
- checkbox: Reorder needed
- rich_text: Notes/serial number

### Views
- Required: table (PRIMARY - full inventory spreadsheet with quantities)
- Optional: board (items grouped by category or condition)
- Optional: gallery (visual item cards with photos)

### Sub-Pages
- "구매 요청서" (Purchase Request): Template for requesting new items with approval workflow
- "폐기 목록" (Disposal Log): Record of disposed/retired items with dates and reasons
- "공급업체 목록" (Supplier Directory): Vendor contacts and pricing information

### Sample Data
Generate 5 inventory items across different categories with realistic Korean office/business data.
Each item needs: relevant icon, quantity, category, location, and price.

## Content Adaptation Examples

**Office Supplies**: Properties → item type, quantity, minimum stock, supplier, reorder date, cost per unit, department
**IT Equipment**: Properties → device type, serial number, assigned to, purchase date, warranty expiry, condition, specs(rich_text)
**Home Inventory**: Properties → room(거실/침실/주방/욕실), brand, purchase price, warranty, receipt photo(url)
**Warehouse Stock**: Properties → SKU, bin location, lot number, expiry date, weight(number), inbound/outbound(select)
**Lab Equipment**: Properties → calibration date, certification, usage hours, maintenance schedule, responsible person

## Formatting Rules

- Callout icon should match context (📦 general, 🖥️ IT, 🏢 office, 🏠 home, 🔧 equipment)
- Table view is the PRIMARY view (quantity tracking needs spreadsheet layout)
- Keep properties under 10 (inventory needs detailed tracking fields)
- Number properties should have appropriate formats (quantity: integer, price: currency)
- Quick stats callout should show key metrics (total items, total value, items needing reorder)

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic purchase dates within ±6 months
- Category values: spread across options (전자기기, 사무용품, 가구, 소모품, 장비)
- Quantity values: realistic varied amounts (3, 15, 50, 120, 2)
- Price values: realistic Korean prices (15,000원, 89,000원, 350,000원, 1,200,000원, 45,000원)
- Location: realistic Korean office locations (3층 서버실, 2층 회의실 A, 1층 창고, 4층 디자인팀, 본사 로비)
- Item names: realistic Korean inventory items (맥북 프로 14인치, A4 복사용지, 회의실 의자, 무선 마우스, 모니터 암)
- Condition: mix of 신품, 양호, 보통, 수리필요

## Pro Design Guide

### Color Palette
- Primary: gray | Accent: blue | Secondary: default
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 📦 전체 물품 수 (callout, blue_background)
  - 💰 총 자산 가치 (callout, blue_background)
  - ⚠️ 재주문 필요 (callout, blue_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "물품을 체계적으로 관리하세요! 재고 현황을 한눈에 📦" (gray_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with table view (기본, 전체 목록), board view (카테고리별), gallery view (물품 카드)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "business" (maps to themed Unsplash cover)
