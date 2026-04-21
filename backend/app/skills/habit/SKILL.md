---
name: habit
description: Creates habit tracking templates with streak counting, daily check-ins, and category-based organization for building consistent routines.
---

# Habit (습관 트래커)

Creates templates for daily habit tracking with streak management and category grouping. Users check off habits daily to visualize consistency and build lasting routines.

## Quick Start

1. **Identify habit context**: What habits does the user want to build or track?
2. **Design properties**: Title + category + checkbox + date + streak + context fields
3. **Set layout**: Single column (focused, distraction-free daily check-in)
4. **Add calendar view**: Essential for visualizing daily completion patterns
5. **Generate samples**: 5-7 realistic habits with mixed completion states

## Template Structure

### Layout
Single column (clean, focused on daily check-in ritual)

### Block Order
1. callout: Motivational message (purple_background, 🎯)
2. empty paragraph (whitespace)
3. column_list:
   - left column (30%):
     - callout: "🔥 연속 달성일" (green_background)
     - callout: "✅ 이번 주 완료율" (green_background)
   - right column (70%):
     - heading_2: Template title (purple)
     - database_ref: Inline database here
4. empty paragraph (whitespace)
5. divider
6. toggle: "📖 사용 가이드" with numbered setup steps
7. toggle: "❓ 자주 묻는 질문" with 2-3 FAQs
8. quote: Motivational closing message

### Database Design

Required properties (always include):
- title: 습관 이름
- select: 카테고리 (건강/학습/생활/마인드/생산성)
- checkbox: 완료 여부
- date: 날짜
- number: 연속일수 (streak count)

Context-dependent properties:
- rich_text: 메모/회고
- select: 시간대 (아침/오후/저녁)
- number: 소요시간 (분)
- select: 난이도 (쉬움/보통/어려움)

### Views
- Required: calendar (일별/주별 완료 패턴 시각화)
- Optional: table (전체 습관 목록 및 연속일수 확인)

### Sub-Pages
- 📋 습관 목표 설정: Monthly/quarterly habit goals and reflection
- 📊 주간 리뷰: Weekly review template for habit assessment

### Sample Data rules
Generate 5-7 items representing a typical week of tracking.
Mix of completed (checked) and incomplete (unchecked) items. Varied categories.

## Content Adaptation Examples

**아침 루틴**: Properties → 기상시간(number), 루틴종류(select: 명상/운동/독서/일기), 소요시간(number), 기분(select)
**운동 습관**: Properties → 운동종류(select: 러닝/웨이트/요가/스트레칭), 시간(number), 칼로리(number), 부위(multi_select)
**학습 습관**: Properties → 과목(select), 학습시간(number), 이해도(select: 상/중/하), 복습여부(checkbox)
**마인드풀니스**: Properties → 유형(select: 명상/감사일기/호흡/산책), 시간(number), 감정상태(select), 메모(rich_text)
**디지털 디톡스**: Properties → 스크린타임(number), SNS차단(checkbox), 독서시간(number), 외출(checkbox)
**재정 습관**: Properties → 유형(select: 가계부/저축/투자공부), 금액(number), 절약여부(checkbox), 메모(rich_text)

## Formatting Rules

- Calendar view is the PRIMARY view (user opens daily to check off)
- Callout icon should be 🎯 or context-appropriate
- Keep properties under 8 (focused, not overwhelming)
- Sample data should show mixed completion states (60-70% checked)
- Streak numbers should be realistic (1-30 range, varied)
- Purple theme conveys mindfulness and self-improvement

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±2 weeks
- Examples: "🧘 아침 명상 10분" (카테고리: 마인드, 연속일수: 12, 완료: true), "📚 30분 독서" (카테고리: 학습, 연속일수: 5, 완료: true), "💪 스트레칭 15분" (카테고리: 건강, 연속일수: 8, 완료: false), "💧 물 2L 마시기" (카테고리: 건강, 연속일수: 21, 완료: true), "📝 감사일기 쓰기" (카테고리: 마인드, 연속일수: 3, 완료: false)
- Checkbox: mix of true and false
- Select values: spread across all categories

## Pro Design Guide

### Color Palette
- Primary: purple | Accent: green | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 🔥 연속 달성일 (callout, green_background)
  - ✅ 이번 주 완료율 (callout, green_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "작은 습관이 인생을 바꿉니다. 오늘도 하나씩 체크해보세요! 🎯" (purple_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with calendar view (기본), table view (상세)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "minimal" (maps to themed Unsplash cover)
