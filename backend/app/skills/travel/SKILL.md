---
name: travel
description: Creates travel planning templates for itineraries, booking management, budget tracking, and packing checklists. Calendar-driven with timeline and table views.
---

# Travel (여행 플래너)

Creates templates for travel planning including itinerary building, booking management, expense tracking, and packing organization.

## Quick Start

1. **Identify travel context**: What does the user want to plan? (itinerary, bookings, budget, packing)
2. **Design properties**: Always include date + select(category) + number(cost). Add context-specific fields.
3. **Set layout**: Two-column (left 30% trip summary / right 70% itinerary DB)
4. **Add calendar view**: Essential for day-by-day itinerary visualization
5. **Generate samples**: 5+ items across travel categories with realistic data

## Template Structure

### Layout
Two-column (left 30% trip summary / right 70% itinerary database)

### Block Order
1. callout: Trip overview message with destination and dates (theme color, context icon)
2. column_list:
   - Column 1 (30%): Trip info callout + budget summary callout
   - Column 2 (70%): Main itinerary content area
3. divider
4. heading_1: Main title (theme color)
5. database_ref: Inline database here
6. toggle: "짐 체크리스트" with packing categories
7. toggle: "비용 정산" with expense summary

### Database Design

Required properties (always include):
- title: Activity/item name
- select: Category (교통/숙소/관광/식당/쇼핑/액티비티)
- date: Date and time
- number: Cost (estimated or actual)
- status: Booking status (미예약/예약중/예약완료/결제완료)
- rich_text: Location/address

Context-dependent properties (AI decides):
- url: Booking link or reference
- rich_text: Confirmation number
- rich_text: Notes/tips
- select: Day (Day1/Day2/Day3/Day4)
- checkbox: Must-visit

### Views
- Required: calendar (PRIMARY - day-by-day itinerary)
- Optional: table (all items with cost totals)
- Optional: board (grouped by booking status)

### Sub-Pages
- "짐 체크리스트" (Packing List): Categorized packing items (의류/세면도구/전자기기/서류)
- "비용 정산" (Expense Summary): Total budget vs actual spending breakdown
- "맛집 & 명소 리스트" (Food & Spots): Curated list of restaurants and attractions

### Sample Data
Generate 5+ items across travel categories with realistic Korean travel data.
Each item needs: relevant icon, category, date, cost, booking status, and location.

## Content Adaptation Examples

**Domestic Trip**: Properties → activity, location, category, cost, day(select), reservation number, rating(select)
**International Trip**: Properties → activity, country/city, category, cost(foreign currency), flight info, visa status(checkbox)
**Budget Travel**: Properties → item, category, estimated cost, actual cost, savings(formula), payment method
**Group Trip**: Properties → activity, participant count, cost per person(number), total cost, organizer, vote(number)

## Formatting Rules

- Callout icon should match context (✈️ flight, 🏨 hotel, 🗺️ sightseeing, 🍽️ food)
- Calendar view is the PRIMARY view (day-by-day planning is key)
- Keep properties under 10 (travel needs quick reference, not complexity)
- Cost properties should use appropriate currency format
- Trip info callout should show destination, dates, total budget

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use consecutive dates for a 3-4 day trip
- Cost values: realistic Korean travel costs (KTX 서울→부산 59,800원, 호텔 1박 120,000원, 해운대 맛집 25,000원, 감천문화마을 입장료 무료, 렌터카 1일 55,000원)
- Category values: spread across 교통, 숙소, 관광, 식당, 쇼핑
- Booking status: mix of 미예약, 예약완료, 결제완료
- Locations: realistic Korean travel destinations (해운대, 감천문화마을, 자갈치시장, 광안리, 범어사)
- Activity names: realistic itinerary items (KTX 이동, 호텔 체크인, 해운대 산책, 돼지국밥 점심, 야경 투어)

## Pro Design Guide

### Color Palette
- Primary: orange | Accent: blue | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - ✈️ 여행지 (callout, blue_background)
  - 📅 여행 기간 (callout, blue_background)
  - 💰 총 예산 (callout, blue_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "설레는 여행을 완벽하게 계획하세요! 모든 일정을 한눈에 ✈️" (orange_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with calendar view (기본, 일정 캘린더), table view (전체 항목), board view (예약 상태)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "travel" (maps to themed Unsplash cover)
