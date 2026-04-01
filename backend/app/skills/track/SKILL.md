---
name: track
description: Creates daily tracking templates for habits, exercise, study, routines, and goals. Checkbox-driven with calendar view.
---

# Track (추적/습관)

Creates templates for daily tracking and habit building. Users check off items daily to build consistency.

## Quick Start

1. **Identify tracking context**: What does the user want to track daily?
2. **Design properties**: Always include checkbox + date. Add context-specific metrics.
3. **Set layout**: Single column (simple, focused)
4. **Add calendar view**: Essential for daily tracking patterns
5. **Generate samples**: 5-7 trackable items with realistic data

## Template Structure

### Layout
Single column (clean, focused on daily check-in)

### Block Order
1. callout: Motivational message (theme color, context icon)
2. divider
3. heading_1: Main title (theme color)
4. database_ref: Inline database here
5. divider
6. toggle: "How to use" with instructions
7. toggle: FAQ items (if applicable)

### Database Design

Required properties (always include):
- title: Item name
- checkbox: Completion status
- date: Tracking date
- select: Category (AI generates based on context)

Context-dependent properties (AI decides):
- number: Duration, count, distance, calories, etc.
- rich_text: Notes/memo
- multi_select: Tags, body parts, tools used

### Views
- Required: calendar (see daily/weekly patterns)
- Optional: table (detailed view with all columns)

### Sub-Pages
Usually none. Track templates are self-contained.

### Sample Data
Generate 5-7 items that represent a typical day/week of tracking.
Each item needs: relevant icon, filled checkbox for some items (show mixed state).

## Content Adaptation Examples

**Exercise**: Properties → type(cardio/strength/flexibility), duration(min), calories, body part
**Study**: Properties → subject, duration, comprehension level, topic
**Habits**: Properties → category(health/learning/lifestyle), streak count
**Diet**: Properties → meal type, calories, protein, carbs
**Water intake**: Properties → time of day, amount(ml), goal reached
**Sleep**: Properties → bedtime, wake time, duration(hrs), quality(1-5), notes
**Mood/Mental Health**: Properties → mood(1-10), energy level, trigger, gratitude note
**Medication**: Properties → medicine name, dosage, time taken, side effects, refill date
**Reading**: Properties → book title, pages read, minutes, notes
**Skincare**: Properties → routine(AM/PM), products used, skin condition, weather

## Formatting Rules

- Callout icon should match context (💪 exercise, 📚 study, 💧 water, 🥗 diet)
- Calendar view is the PRIMARY view (user opens this daily)
- Keep properties under 7 (focused, not overwhelming)
- Sample data should show mixed completion states (some checked, some not)

## Color Theme Guide

Recommended color combinations by context:
- Exercise/Sports: orange (energetic, warm) — callout: orange_background, headings: orange
- Study/Learning: blue (calm, focused) — callout: blue_background, headings: blue
- Habits/Lifestyle: purple (creative, mindful) — callout: purple_background, headings: purple
- Diet/Nutrition: green (healthy, natural) — callout: green_background, headings: green
- Water/Hydration: blue (refreshing, clean) — callout: blue_background, headings: blue
- Sleep/Rest: purple (calming, nighttime) — callout: purple_background, headings: purple
- Mental Health/Mood: pink (gentle, emotional) — callout: pink_background, headings: pink
- Finance/Spending: yellow (attention, money) — callout: yellow_background, headings: yellow
- Default: gray (neutral, clean)

## Complexity Levels

### Simple (5-8 blocks): Quick tracker
callout → heading_1 → database_ref → toggle(usage tip)

### Medium (10-15 blocks): Standard tracker
callout → divider → heading_2(intro) → paragraph → heading_1 → database_ref → divider → toggle(usage) → toggle(FAQ)

### Complex (20-30 blocks): Full tracking system
callout → quote(motivational motto) → divider → column_list(weekly stats sidebar + main tracker) → heading_1 → database_ref → divider → heading_2(guide) → numbered_list(steps) → to_do(daily checklist) → toggle(FAQ x3) → toggle(advanced tips) → toggle(milestone rewards)

## Cross-Skill Combinations

- track + collect: "운동하면서 식단도 기록" — Use track for daily exercise log DB + collect for meal/recipe collection DB
- track + plan: "시험 준비 + 공부 기록" — Use plan for study schedule & milestones + track for daily study hours log
- track + hub: "여러 습관을 한 곳에서" — Use hub as central dashboard + track DBs for each habit area (exercise, reading, meditation)
- track + manage: "팀 운동 챌린지" — Use manage for challenge pipeline/status + track for individual daily check-ins
- track + guide: "습관 만들기 가이드 + 추적" — Use guide for habit-building onboarding doc + track for the actual daily tracker

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±2 weeks
- Status values: spread across all statuses (시작 전, 진행 중, 완료)
- Select values: use different options for variety
- Number values: use realistic, varied numbers
- Checkbox: mix of true and false

## Pro Design Guide

### Color Palette
- Primary: orange | Accent: green | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 📊 이번 주 완료율 (callout, green_background)
  - 🔥 연속 달성일 (callout, green_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "오늘도 꾸준히! 매일의 기록이 변화를 만듭니다 💪" (orange_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with calendar view (기본), table view (상세)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "fitness" (maps to themed Unsplash cover)
