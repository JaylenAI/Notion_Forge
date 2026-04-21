---
name: budget
description: Creates household budget and expense tracking templates for income, spending, savings, and category-based financial analysis. Number-driven with table and calendar views.
---

# Budget (가계부)

Creates templates for household budget management including income/expense tracking, savings goals, and category-based spending analysis.

## Quick Start

1. **Identify budget context**: What does the user want to track? (daily expenses, monthly budget, savings, category analysis)
2. **Design properties**: Always include number(amount) + date + select(category) + select(type). Add context-specific fields.
3. **Set layout**: Two-column (left 30% summary callouts / right 70% DB)
4. **Add table view**: Essential for financial data with totals
5. **Generate samples**: 5+ items with realistic Korean household expenses

## Template Structure

### Layout
Two-column (left 30% summary callouts / right 70% database)

### Block Order
1. callout: Monthly budget overview (theme color, context icon)
2. column_list:
   - Column 1 (30%): Monthly income callout + expense callout + savings callout
   - Column 2 (70%): Main content area
3. divider
4. heading_1: Main title (theme color)
5. database_ref: Inline database here
6. toggle: "월별 정산 가이드" with settlement tips
7. toggle: "절약 팁" with saving advice

### Database Design

Required properties (always include):
- title: Transaction name
- number: Amount (currency format)
- select: Type (수입/지출/저축)
- select: Category (식비/교통/문화/생활/의료/쇼핑/급여/부수입)
- date: Transaction date
- select: Payment method (현금/신용카드/체크카드/계좌이체)

Context-dependent properties (AI decides):
- rich_text: Memo/notes
- checkbox: Recurring (fixed expense)
- checkbox: Necessary expense
- url: Receipt link or proof

### Views
- Required: table (PRIMARY - all transactions with totals)
- Optional: calendar (monthly spending overview)
- Optional: board (category-grouped spending)

### Sub-Pages
- "월별 정산" (Monthly Settlement): Summary of monthly income vs expenses with balance
- "저축 목표" (Savings Goals): Target amounts, progress, and deadline tracking
- "고정 지출 관리" (Fixed Expenses): Recurring bills and subscriptions list

### Sample Data
Generate 5+ items representing realistic Korean household transactions.
Each item needs: relevant icon, filled amount, category, type, payment method, and date.

## Content Adaptation Examples

**Daily Expense**: Properties → item, amount, category(식비/교통/문화), payment method, date, memo
**Monthly Budget**: Properties → category, budget limit(number), spent(number), remaining(formula), month(select)
**Savings Tracker**: Properties → goal name, target amount, current amount, progress(formula), deadline(date)
**Subscription**: Properties → service name, monthly fee, billing date, auto-renewal(checkbox), platform

## Formatting Rules

- Callout icon should match context (💰 budget, 💳 expense, 🏦 savings, 📊 analysis)
- Table view is the PRIMARY view (financial data needs columns and totals)
- Keep properties under 10 (detailed but not overwhelming)
- Number properties should use Korean Won format (원)
- Summary callouts should show key totals (이번 달 수입, 지출, 잔액)
- Parent skill is finance; inherit green color theme

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within current month
- Amount values: realistic Korean household amounts (편의점 4,200원, 점심 식사 8,500원, 교통카드 충전 50,000원, 월세 700,000원, 넷플릭스 17,000원, 급여 3,200,000원)
- Category values: spread across 식비, 교통, 문화, 생활, 쇼핑, 급여
- Type values: mix of 수입, 지출, 저축
- Payment method: mix of 신용카드, 체크카드, 계좌이체, 현금
- Recurring: mark fixed expenses like 월세, 구독 as true

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
  - 🏦 이번 달 저축 (callout, yellow_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "알뜰한 살림의 시작! 수입과 지출을 꼼꼼히 기록하세요 💰" (green_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with table view (기본, 전체 내역), calendar view (월별 보기)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "finance" (maps to themed Unsplash cover)
