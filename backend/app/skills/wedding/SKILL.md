---
name: wedding
description: Creates wedding planning templates for budget tracking, vendor management, timeline coordination, and checklist organization. Status-driven with board and table views.
---

# Wedding (결혼 준비)

Creates templates for wedding planning including budget management, vendor coordination, timeline tracking, and preparation checklists.

## Quick Start

1. **Identify wedding context**: What does the user want to manage? (budget, vendors, timeline, guest list, checklist)
2. **Design properties**: Always include status + number(budget) + date. Add context-specific fields.
3. **Set layout**: Two-column (left 30% D-Day stats / right 70% planning DB)
4. **Add board view**: Essential for status-based progress tracking
5. **Generate samples**: 5+ items across different wedding categories with realistic data

## Template Structure

### Layout
Two-column (left 30% D-Day & budget stats / right 70% planning database)

### Block Order
1. callout: D-Day countdown message (theme color, context icon)
2. column_list:
   - Column 1 (30%): D-Day countdown callout + budget summary callout
   - Column 2 (70%): Main planning content area
3. divider
4. heading_1: Main title (theme color)
5. database_ref: Inline database here
6. toggle: "예산 총정리" with budget breakdown
7. toggle: "체크리스트" with preparation checklist

### Database Design

Required properties (always include):
- title: Item name
- select: Category (예식장/드레스/촬영/청첩장/예물/신혼여행/혼수/헤어메이크업)
- number: Budget (planned amount)
- number: Actual cost
- status: Progress (미시작/알아보는중/예약완료/결제완료)
- date: Deadline or appointment date

Context-dependent properties (AI decides):
- rich_text: Vendor name/contact
- url: Reference link or portfolio
- rich_text: Notes/reviews
- checkbox: Contract signed
- select: Priority (필수/선택/보류)

### Views
- Required: board (PRIMARY - progress tracking by status)
- Optional: table (full budget comparison with all columns)
- Optional: calendar (appointment and deadline calendar)

### Sub-Pages
- "하객 명단" (Guest List): Guest names, relationship, attendance confirmation, gift tracking
- "예산 상세" (Budget Details): Detailed cost breakdown per category with quotes
- "웨딩 타임라인" (Wedding Timeline): Day-of schedule from preparation to reception

### Sample Data
Generate 5+ items across wedding categories with realistic Korean wedding data.
Each item needs: relevant icon, category, budget, actual cost, status, and date.

## Content Adaptation Examples

**Budget Planner**: Properties → item, category, estimated cost, actual cost, difference(formula), payment status, vendor
**Vendor Management**: Properties → vendor name, category, contact, quote(number), rating(select), contract status(checkbox)
**Guest List**: Properties → name, relationship(select), party(신랑측/신부측), attendance(select), meal choice, gift amount(number)
**Day-of Timeline**: Properties → time slot, activity, location, responsible person, duration(number), notes

## Formatting Rules

- Callout icon should match context (💒 ceremony, 💍 engagement, 👰 bride, 📸 photo)
- Board view is the PRIMARY view (progress tracking is key for wedding prep)
- Keep properties under 10 (wedding has many items, keep each entry manageable)
- Budget properties should show Korean Won format (원)
- D-Day callout should prominently display countdown

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates spread across 3-6 months ahead
- Budget values: realistic Korean wedding costs (예식장 800만원, 스튜디오 촬영 250만원, 드레스 대여 180만원, 신혼여행 350만원, 청첩장 30만원, 예물 500만원)
- Status values: spread across 미시작, 알아보는중, 예약완료, 결제완료
- Category values: spread across 예식장, 드레스, 촬영, 청첩장, 예물, 신혼여행
- Vendor info: realistic Korean vendor names (라움웨딩홀, 로자스튜디오, 베라왕 청담, 하나투어)
- Priority: mix of 필수 and 선택 items

## Pro Design Guide

### Color Palette
- Primary: pink | Accent: purple | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 💒 D-Day (callout, purple_background)
  - 💰 총 예산 (callout, purple_background)
  - ✅ 완료 항목 (callout, purple_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "인생에서 가장 빛나는 날을 완벽하게 준비하세요! 💒" (pink_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with board view (기본, 진행 상태), table view (예산 비교), calendar view (일정)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "minimal" (maps to themed Unsplash cover)
