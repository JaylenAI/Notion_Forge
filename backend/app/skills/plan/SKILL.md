---
name: plan
description: Creates planning templates with checklists and schedules. Wedding prep, travel planning, moving, exams, events, goal planning.
---

# Plan (계획/일정)

Creates templates for planning events or goals with checklists and timeline. Combines checklist sections with a database for detailed tracking.

## Quick Start

1. **Identify planning context**: What event/goal is being planned?
2. **Design checklist sections**: Group tasks by phase/category
3. **Set layout**: Single column (timeline-focused)
4. **Add calendar view**: Date-driven planning needs calendar
5. **Generate samples**: Mix of checked and unchecked items

## Template Structure

### Layout
Single column (sequential, timeline flow)

### Block Order
1. callout: Planning overview (theme color, context icon)
2. divider
3. heading_2: Phase/Category 1 (theme color) + to_do items
4. heading_2: Phase/Category 2 (theme color) + to_do items
5. heading_2: Phase/Category 3 (theme color) + to_do items
6. divider
7. heading_1: Detailed tracker title (theme color)
8. database_ref: Inline database here
9. divider
10. toggle: FAQ / tips

### Database Design

Required properties:
- title: Task/item name
- date: Due date / D-day
- checkbox: Completion
- select: Category/phase

Context-dependent:
- number: Budget/cost
- rich_text: Notes, assignee
- select: Priority

### Views
- Required: calendar (date-based planning)
- Optional: table (checklist view)

### Sub-Pages
Usually none.

### Sample Data
Generate 5 items with mix of completed (early items) and pending (later items).

## Content Adaptation Examples

**Wedding**: Phases → Venue/Dress/Invitation/Ceremony/Honeymoon, Properties → budget, vendor, D-day
**Travel**: Phases → Flights/Hotel/Activities/Packing, Properties → cost, booking status, date
**Moving**: Phases → Before/During/After move, Properties → cost, deadline, assignee
**Exam**: Phases → by subject or by week, Properties → study hours, confidence level, material
**Event**: Phases → Preparation/Setup/Day-of/Follow-up, Properties → budget, assignee, deadline

## Formatting Rules

- Checklist sections should show logical progression (early → late)
- Some to_do items should be pre-checked (show progress)
- D-day or deadline should be prominent
- Calendar view for timeline overview

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±2 weeks
- Status values: spread across all statuses (시작 전, 진행 중, 완료)
- Select values: use different options for variety
- Number values: use realistic, varied numbers
- Checkbox: mix of true and false
