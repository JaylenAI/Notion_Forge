---
name: health
description: Creates health tracking templates for sleep, weight, blood pressure, water intake, and vital metrics with trend visualization.
---

# Health (건강 관리)

Creates templates for tracking daily health metrics including sleep, weight, blood pressure, water intake, and overall wellness. Designed for consistent self-monitoring and long-term health trend analysis.

## Quick Start

1. **Identify health context**: What health metrics does the user want to track?
2. **Design properties**: Title + metric type + value + unit + date + context fields
3. **Set layout**: Single column (clean, clinical-yet-friendly)
4. **Add table view**: Primary view for numerical data comparison
5. **Generate samples**: 5-7 realistic health entries across metric types

## Template Structure

### Layout
Single column (organized, data-focused with warm tone)

### Block Order
1. callout: Wellness message (blue_background, 💚)
2. empty paragraph (whitespace)
3. column_list:
   - left column (30%):
     - callout: "😴 평균 수면시간" (green_background)
     - callout: "💧 일일 수분섭취" (green_background)
   - right column (70%):
     - heading_2: Template title (blue)
     - database_ref: Inline database here
4. empty paragraph (whitespace)
5. divider
6. toggle: "📖 사용 가이드" with numbered setup steps
7. toggle: "❓ 자주 묻는 질문" with 2-3 FAQs
8. quote: Health motivation closing message

### Database Design

Required properties (always include):
- title: 기록 항목
- select: 유형 (수면/체중/혈압/수분/운동/컨디션)
- number: 수치
- rich_text: 단위
- date: 날짜

Context-dependent properties:
- rich_text: 메모/증상
- select: 컨디션 (최상/좋음/보통/나쁨/최하)
- number: 목표치
- checkbox: 목표달성 여부
- select: 시간대 (기상후/오전/오후/취침전)

### Views
- Required: table (수치 비교 및 필터링에 최적)
- Optional: calendar (날짜별 기록 확인), board (유형별 그룹핑)

### Sub-Pages
- 🎯 건강 목표: Monthly health goals and target metrics
- 📋 검진 기록: Annual checkup results and doctor notes

### Sample Data rules
Generate 5-7 items across different health metric types.
Include varied metrics (sleep hours, weight kg, blood pressure, water ml).

## Content Adaptation Examples

**수면 추적**: Properties → 취침시간(rich_text), 기상시간(rich_text), 수면시간(number/hrs), 수면질(select: 상/중/하), 꿈기록(rich_text)
**체중 관리**: Properties → 체중(number/kg), 체지방률(number/%), 근육량(number/kg), 목표체중(number), BMI(number)
**혈압 관리**: Properties → 수축기(number), 이완기(number), 맥박(number), 측정시간(select), 복약여부(checkbox)
**수분 섭취**: Properties → 섭취량(number/ml), 목표량(number), 음료종류(select: 물/차/커피/주스), 달성률(number/%)
**컨디션 체크**: Properties → 에너지(select: 1-5), 스트레스(select: 1-5), 통증부위(multi_select), 특이사항(rich_text)

## Formatting Rules

- Table view is the PRIMARY view (numerical data requires columns)
- Callout icon should be 💚 or health-related (💪😴💧)
- Keep properties under 8 per metric type
- Blue theme conveys trust, calmness, and medical precision
- Sample data should use realistic Korean adult health ranges
- Units should always be explicit (kg, mmHg, ml, hrs)

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±2 weeks
- Examples: "😴 수면 기록" (유형: 수면, 수치: 7.5, 단위: 시간, 컨디션: 좋음), "⚖️ 체중 측정" (유형: 체중, 수치: 68.2, 단위: kg, 목표달성: false), "💧 수분 섭취" (유형: 수분, 수치: 1800, 단위: ml, 목표달성: true), "❤️ 혈압 측정" (유형: 혈압, 수치: 120, 단위: mmHg, 컨디션: 보통), "🏃 운동 기록" (유형: 운동, 수치: 45, 단위: 분, 컨디션: 최상)
- Number values: use realistic, medically reasonable ranges
- Select values: spread across all categories

## Pro Design Guide

### Color Palette
- Primary: blue | Accent: green | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 😴 평균 수면시간 (callout, green_background)
  - 💧 일일 수분섭취 (callout, green_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "건강한 하루의 시작! 매일 기록하면 몸이 보내는 신호가 보입니다 💚" (blue_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with table view (기본), calendar view (달력)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "nature" (maps to themed Unsplash cover)
