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

## Formatting Rules

- Callout icon should match context (💪 exercise, 📚 study, 💧 water, 🥗 diet)
- Calendar view is the PRIMARY view (user opens this daily)
- Keep properties under 7 (focused, not overwhelming)
- Sample data should show mixed completion states (some checked, some not)

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±2 weeks
- Status values: spread across all statuses (시작 전, 진행 중, 완료)
- Select values: use different options for variety
- Number values: use realistic, varied numbers
- Checkbox: mix of true and false
