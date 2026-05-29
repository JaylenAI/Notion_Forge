---
name: finance
description: Creates financial management templates for budgets, expenses, subscriptions, and investments. Number-driven with table view.
---

# Finance (가계부/재무)

Creates templates for financial management including budgets, expense tracking, subscription management, and investment portfolios.

## Quick Start

1. **Identify financial context**: What does the user want to manage? (expenses, budget, investments, subscriptions)
2. **Design properties**: Always include number(amount) + date + select(category). Add context-specific fields.
3. **Set layout**: Two-column (left 30% summary callouts / right 70% DB)
4. **Add table view**: Essential for financial data analysis
5. **Generate samples**: 5+ items with realistic Korean financial data

## Template Structure

### Layout
Two-column (left 30% summary callouts / right 70% database)

### Block Order
1. callout: Monthly summary message (theme color, context icon)
2. column_list:
   - Column 1 (30%): Budget overview callout + category chart callout
   - Column 2 (70%): Main content area
3. heading_1: Main title (theme color)
4. database_ref: Inline database here
5. divider
6. toggle: "Tips for better financial management" with instructions

### Database Design

Required properties (always include):
- title: Item name
- number: Amount (currency format)
- select: Category (식비/교통/문화/생활/의료/쇼핑)
- date: Transaction date
- select: Type (수입/지출/투자)

Context-dependent properties (AI decides):
- rich_text: Memo/notes
- checkbox: Recurring transaction
- url: Receipt link
- select: Payment method (현금/카드/계좌이체)

### Views
- Required: table (PRIMARY - detailed financial overview with all columns)
- Optional: calendar (monthly overview of transactions)

### Sub-Pages
- "월별 정산" (Monthly Settlement): Summary of monthly income/expenses
- "저축 목표" (Savings Goals): Target amounts and progress tracking

### Sample Data
Generate 5+ items that represent realistic Korean financial transactions.
Each item needs: relevant icon, filled amount, category, type, and date.

## Content Adaptation Examples

**Budget**: Properties → category(식비/교통/문화/생활), budget limit, spent amount, remaining
**Subscription**: Properties → service name, monthly fee, billing date, auto-renewal, platform(Netflix/Spotify/gym)
**Investment**: Properties → asset type(stock/fund/crypto), buy price, current price, return rate, quantity
**Expense**: Properties → amount, category, payment method, receipt, daily/weekly/monthly

## Formatting Rules

- Callout icon should match context (💰 budget, 💳 expense, 📊 investment, 🔄 subscription)
- Table view is the PRIMARY view (financial data needs columns)
- Keep properties under 8 (focused, not overwhelming)
- Number properties should use Korean Won format where applicable
- Summary callouts should show key totals (monthly spend, budget remaining)

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±2 weeks
- Amount values: use realistic Korean Won amounts (카페라떼 5,800원, 월세 650,000원, 점심 식사 9,500원, 교통카드 충전 50,000원, 넷플릭스 17,000원)
- Select values: spread across all categories and types
- Type values: mix of 수입, 지출, and 투자
- Checkbox: mix of recurring (true) and one-time (false) transactions

## Pro Design Guide

### Color Palette
- Primary: green | Accent: yellow | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 💰 이번 달 수입 (callout, yellow_background)
  - 💸 이번 달 지출 (callout, yellow_background)
  - 💎 저축 목표 (callout, yellow_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "똑똑한 돈 관리의 시작! 수입과 지출을 한눈에 파악하세요 💰" (green_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with table view (기본, 전체 거래 내역), calendar view (월별)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Required Calculated Properties (필수 — 유료급 차별점)
거래 내역 DB에 **계산 속성을 반드시 포함**하라. 단순 입력값 나열이 아닌 자동 계산이 유료 템플릿의 핵심이다.
- `부호금액` (formula): 수입/지출 부호 반영 — `{"type": "formula", "expression": "if(prop(\"구분\") == \"지출\", prop(\"금액\") * -1, prop(\"금액\"))"}`
- 카테고리 예산 DB를 함께 둘 경우(권장, 멀티 DB):
  - 거래내역에 `카테고리`(relation → 카테고리예산), 카테고리예산에 `거래목록`(relation → 거래내역)
  - 카테고리예산 `사용액` (rollup): `{"type": "rollup", "relation_property": "거래목록", "target_property": "금액", "function": "sum"}`
  - 카테고리예산 `잔액` (formula): `{"type": "formula", "expression": "prop(\"월예산\") - prop(\"사용액\")"}`

### Cover Image Category
cover_category: "finance" (maps to themed Unsplash cover)
