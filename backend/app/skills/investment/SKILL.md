---
name: investment
description: Creates investment portfolio management templates for stock tracking, asset allocation, returns analysis, and rebalancing. Table-driven with board and timeline views.
---

# Investment (투자 포트폴리오)

Creates templates for investment portfolio management including stock/ETF tracking, returns monitoring, asset allocation, and rebalancing records.

## Quick Start

1. **Identify investment context**: What does the user invest in? (stocks, ETFs, crypto, funds, real estate)
2. **Design properties**: Always include number(buy price) + number(quantity) + select(category). Add context-specific fields.
3. **Set layout**: Two-column (left 25% portfolio summary / right 75% holdings DB)
4. **Add table view**: Essential for numerical portfolio data with returns
5. **Generate samples**: 5 holdings across different asset classes with realistic market data

## Template Structure

### Layout
Two-column (left 25% portfolio overview / right 75% holdings database)

### Block Order
1. callout: Portfolio management intro message (theme color, context icon)
2. column_list:
   - Column 1 (25%): Total value callout + total return callout + asset allocation callout
   - Column 2 (75%): Main portfolio content area
3. divider
4. heading_1: Main title (theme color)
5. database_ref: Inline database here
6. toggle: "투자 원칙 & 전략" with personal investment rules and rebalancing guide

### Database Design

Required properties (always include):
- title: Asset/stock name
- number: Buy price (per unit)
- number: Quantity/shares
- select: Category (국내주식/해외주식/ETF/펀드/채권/코인/부동산)
- date: Purchase date

Context-dependent properties (AI decides):
- number: Current price
- number: Total invested amount
- number: Current value
- number: Return rate (%)
- number: Return amount (profit/loss)
- select: Sector (IT/금융/헬스케어/에너지/소비재/산업재)
- select: Risk level (공격/중립/안정)
- rich_text: Ticker symbol
- rich_text: Investment thesis/notes
- checkbox: Active position
- date: Target sell date

### Views
- Required: table (PRIMARY - numerical portfolio spreadsheet with returns)
- Optional: board (holdings grouped by category or sector)
- Optional: timeline (purchase dates and holding periods)

### Sub-Pages
- "리밸런싱 기록" (Rebalancing Log): History of portfolio adjustments with rationale
- "배당금 추적" (Dividend Tracker): Dividend income records by stock and date
- "투자 일지" (Investment Journal): Trade rationale, market observations, and lessons learned

### Sample Data
Generate 5 holdings across different asset classes with realistic Korean market data.
Each item needs: relevant icon, buy price, quantity, category, return rate, and purchase date.

## Content Adaptation Examples

**Korean Stocks**: Properties → ticker, sector, buy price(KRW), shares, current price, return%, dividend yield, market cap tier
**US Stocks**: Properties → ticker, exchange(NYSE/NASDAQ), buy price(USD), shares, fx rate, return%(KRW), sector
**ETF Portfolio**: Properties → ETF name, tracking index, expense ratio, buy price, shares, allocation%, rebalance date
**Crypto Portfolio**: Properties → coin name, exchange(업비트/바이낸스), buy price, amount, wallet(hot/cold), market cap rank
**Real Estate**: Properties → property type, location, purchase price, current value, monthly rent, cap rate(%), loan balance
**Retirement Fund**: Properties → fund name, contribution/month, total invested, current value, target allocation%, risk level

## Formatting Rules

- Callout icon should match context (📈 stocks, 💰 general, 🪙 crypto, 🏠 real estate, 💵 dividend)
- Table view is the PRIMARY view (numbers and returns need spreadsheet precision)
- Keep properties under 10 (financial data needs detail but avoid overload)
- Number formats: prices in KRW with comma separator, return rate in % with 2 decimals
- Quick stats callout should show key metrics (total value, total return, best performer)

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic purchase dates within ±6 months
- Category values: spread across options (국내주식, 해외주식, ETF, 코인, 펀드)
- Buy prices: realistic Korean market prices (삼성전자 72,000원, TIGER S&P500 18,500원, 비트코인 52,000,000원)
- Quantities: realistic varied amounts (10주, 50주, 100주, 0.5BTC, 200좌)
- Return rates: realistic mixed returns (+12.5%, -3.2%, +28.7%, +5.1%, -8.4%)
- Sector values: different sectors (IT, 금융, 헬스케어, 에너지, 소비재)
- Asset names: realistic Korean investment names (삼성전자, TIGER 미국S&P500, 카카오, 테슬라, KODEX 200)
- Risk levels: mix of 공격, 중립, 안정

## Pro Design Guide

### Color Palette
- Primary: green | Accent: blue | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 💰 총 투자금 (callout, blue_background)
  - 📈 총 수익률 (callout, blue_background)
  - 🏆 최고 수익 종목 (callout, blue_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "나의 투자 현황을 한눈에! 체계적인 포트폴리오 관리를 시작하세요 📈" (green_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with table view (기본, 포트폴리오), board view (카테고리별), timeline view (매수 일정)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "finance" (maps to themed Unsplash cover)
