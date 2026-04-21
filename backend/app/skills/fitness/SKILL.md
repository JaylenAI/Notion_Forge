---
name: fitness
description: Creates workout and fitness tracking templates for exercise logs, calorie tracking, body part analysis, and weekly reports. Number-driven with calendar and table views.
---

# Fitness (운동 기록)

Creates templates for fitness tracking including workout logs, calorie management, body part targeting, and progress analysis.

## Quick Start

1. **Identify fitness context**: What does the user want to track? (workouts, calories, body measurements, weekly goals)
2. **Design properties**: Always include select(type) + number(duration) + date. Add context-specific fields.
3. **Set layout**: Two-column (left 30% today's stats / right 70% workout DB)
4. **Add calendar view**: Essential for workout consistency visualization
5. **Generate samples**: 5+ workouts across different types with realistic data

## Template Structure

### Layout
Two-column (left 30% today's stats / right 70% workout database)

### Block Order
1. callout: Fitness motivation message (theme color, context icon)
2. column_list:
   - Column 1 (30%): Weekly goal callout + streak callout
   - Column 2 (70%): Main workout content area
3. divider
4. heading_1: Main title (theme color)
5. database_ref: Inline database here
6. toggle: "주간 운동 리포트" with weekly summary template
7. toggle: "운동 루틴 가이드" with recommended routines

### Database Design

Required properties (always include):
- title: Exercise name
- select: Type (유산소/근력/유연성/HIIT/스포츠)
- number: Duration (minutes)
- number: Calories burned
- multi_select: Body part (가슴/등/어깨/팔/하체/코어/전신)
- date: Workout date
- checkbox: Completed

Context-dependent properties (AI decides):
- number: Sets
- number: Reps
- number: Weight (kg)
- select: Intensity (가볍게/보통/강하게/최대)
- rich_text: Notes/condition

### Views
- Required: calendar (PRIMARY - workout consistency at a glance)
- Optional: table (all workout details with filtering)
- Optional: board (grouped by body part or type)

### Sub-Pages
- "주간 리포트" (Weekly Report): Weekly workout summary with total time, calories, and targets
- "운동 루틴" (Workout Routines): Predefined routines for different goals (근력/다이어트/유연성)
- "신체 기록" (Body Measurements): Weight, body fat, muscle mass tracking over time

### Sample Data
Generate 5+ workouts across different types with realistic Korean fitness data.
Each item needs: relevant icon, type, duration, calories, body part, and date.

## Content Adaptation Examples

**Gym Workout**: Properties → exercise, type(근력), sets, reps, weight(kg), body part, rest time(number)
**Running Log**: Properties → distance(km), pace(min/km), duration, heart rate(number), route(rich_text), weather(select)
**Diet Tracker**: Properties → meal name, calories, protein(g), carbs(g), fat(g), meal type(아침/점심/저녁/간식)
**Yoga/Stretch**: Properties → pose name, duration, flexibility level(select), body part, breathing notes

## Formatting Rules

- Callout icon should match context (🏋️ gym, 🏃 running, 🧘 yoga, 💪 fitness)
- Calendar view is the PRIMARY view (consistency tracking is key)
- Keep properties under 10 (quick logging, not overwhelming)
- Number properties should include units (분, kcal, kg, 회)
- Quick stats callout should show weekly totals (이번 주 운동 횟수, 총 칼로리, 연속 일수)

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates across the current week
- Exercise names: realistic Korean workout names (벤치프레스, 스쿼트, 러닝머신 30분, 플랭크, 데드리프트, 요가 스트레칭)
- Duration values: realistic times (30분, 45분, 60분, 20분, 90분)
- Calorie values: realistic burn amounts (150kcal, 320kcal, 450kcal, 200kcal, 550kcal)
- Body parts: mix across 가슴, 등, 하체, 코어, 전신
- Type values: spread across 유산소, 근력, 유연성

## Pro Design Guide

### Color Palette
- Primary: orange | Accent: green | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 🏋️ 이번 주 운동 (callout, green_background)
  - 🔥 소모 칼로리 (callout, green_background)
  - 🔗 연속 기록 (callout, green_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "꾸준함이 최고의 운동입니다! 오늘도 기록하세요 💪" (orange_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with calendar view (기본, 운동 캘린더), table view (상세 기록)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "fitness" (maps to themed Unsplash cover)
