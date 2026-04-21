---
name: diet
description: Creates meal planning and nutrition tracking templates with calorie counting, macros management, and meal-type categorization.
---

# Diet (식단/다이어트)

Creates templates for daily meal logging and nutritional tracking. Users record meals with calorie and macro breakdowns to maintain balanced eating habits and achieve diet goals.

## Quick Start

1. **Identify diet context**: What nutritional goals does the user have?
2. **Design properties**: Title + meal type + calories + macros + date + context fields
3. **Set layout**: Single column (clean, daily meal log format)
4. **Add table view**: Primary view for nutritional data comparison
5. **Generate samples**: 5-7 realistic Korean meals with accurate nutritional data

## Template Structure

### Layout
Single column (organized, meal-log focused)

### Block Order
1. callout: Healthy eating message (green_background, 🥗)
2. empty paragraph (whitespace)
3. column_list:
   - left column (30%):
     - callout: "🔥 오늘 섭취 칼로리" (orange_background)
     - callout: "🎯 일일 목표 달성률" (orange_background)
   - right column (70%):
     - heading_2: Template title (green)
     - database_ref: Inline database here
4. empty paragraph (whitespace)
5. divider
6. toggle: "📖 사용 가이드" with numbered setup steps
7. toggle: "❓ 자주 묻는 질문" with 2-3 FAQs
8. quote: Healthy eating closing message

### Database Design

Required properties (always include):
- title: 음식 이름
- select: 구분 (아침/점심/저녁/간식/야식)
- number: 칼로리 (kcal)
- number: 단백질 (g)
- date: 날짜

Context-dependent properties:
- number: 탄수화물 (g)
- number: 지방 (g)
- rich_text: 메모/재료
- checkbox: 건강식 여부
- select: 조리방식 (직접요리/배달/외식/편의점)
- multi_select: 태그 (고단백/저탄수/비건/글루텐프리)

### Views
- Required: table (영양소 수치 비교 필수)
- Optional: calendar (날짜별 식단 확인), gallery (음식 사진 브라우징)

### Sub-Pages
- 📋 주간 식단 계획: Weekly meal prep plan and grocery list
- 🎯 식단 목표: Monthly calorie/macro targets and progress

### Sample Data rules
Generate 5-7 items representing meals across a typical day.
Include breakfast, lunch, dinner, and snacks with realistic Korean food data.

## Content Adaptation Examples

**다이어트 식단**: Properties → 칼로리(number), 단백질(number), 탄수화물(number), 지방(number), 목표칼로리대비(select: 초과/적정/부족)
**벌크업 식단**: Properties → 총칼로리(number), 단백질(number), 식사횟수(number), 보충제(checkbox), 체중변화(number)
**비건 식단**: Properties → 식물성단백질(number), 비건등급(select: 비건/락토/페스코), 영양제복용(checkbox), 대체식품(rich_text)
**간헐적 단식**: Properties → 단식시작(rich_text), 단식종료(rich_text), 단식시간(number/hrs), 식사창(select: 16:8/18:6/20:4), 공복감(select)
**아기 이유식**: Properties → 단계(select: 초기/중기/후기/완료기), 재료(multi_select), 알레르기반응(checkbox), 섭취량(select)
**당뇨 식단**: Properties → 혈당(number), GI지수(select: 저/중/고), 탄수화물(number), 식이섬유(number), 인슐린(checkbox)

## Formatting Rules

- Table view is the PRIMARY view (nutritional numbers need columns)
- Callout icon should be 🥗 or food-related (🍱🥑🔥)
- Green theme conveys health, freshness, and natural eating
- Sample data should use realistic Korean food calorie values
- Meal types should cover full day (아침/점심/저녁/간식)
- Nutritional values must be medically reasonable

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±2 weeks
- Examples: "🍚 현미밥 + 된장찌개 + 제육볶음" (구분: 점심, 칼로리: 620, 단백질: 28, 건강식: true), "🥗 닭가슴살 샐러드" (구분: 저녁, 칼로리: 350, 단백질: 35, 건강식: true), "🍳 계란 토스트 + 우유" (구분: 아침, 칼로리: 420, 단백질: 18, 건강식: true), "🍫 프로틴바 + 아메리카노" (구분: 간식, 칼로리: 230, 단백질: 20, 건강식: true), "🍜 김치찌개 + 공기밥" (구분: 저녁, 칼로리: 480, 단백질: 22, 건강식: false)
- Number values: use realistic calorie ranges (200-800 per meal)
- Select values: spread across all meal types

## Pro Design Guide

### Color Palette
- Primary: green | Accent: orange | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 🔥 오늘 섭취 칼로리 (callout, orange_background)
  - 🎯 일일 목표 달성률 (callout, orange_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "오늘 뭐 먹었지? 기록하면 식습관이 보입니다 🥗" (green_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with table view (기본), calendar view (달력)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "food" (maps to themed Unsplash cover)
