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
**Home Renovation**: Phases → Design/Demolition/Construction/Finishing/Inspection, Properties → contractor, cost, room, timeline
**Fitness Challenge**: Phases → Week 1-4 progressive overload, Properties → target, actual, body measurement, diet plan
**Product Launch**: Phases → Research/Design/Development/Beta/Launch, Properties → owner, status, budget, launch date
**Party/Celebration**: Phases → Theme/Venue/Invitations/Food/Decorations/Day-of, Properties → budget, guest count, vendor
**New Year Goals**: Phases → Q1/Q2/Q3/Q4, Properties → goal area(health/career/finance/personal), milestone, progress

## Formatting Rules

- Checklist sections should show logical progression (early → late)
- Some to_do items should be pre-checked (show progress)
- D-day or deadline should be prominent
- Calendar view for timeline overview

## Color Theme Guide

Recommended color combinations by context:
- Wedding: pink (romantic, celebratory) — callout: pink_background, headings: pink
- Travel: orange (adventurous, exciting) — callout: orange_background, headings: orange
- Moving: yellow (transition, new beginning) — callout: yellow_background, headings: yellow
- Exam/Study: blue (focused, calm) — callout: blue_background, headings: blue
- Event Planning: purple (creative, festive) — callout: purple_background, headings: purple
- Goal Setting: green (growth, achievement) — callout: green_background, headings: green
- Home Renovation: brown/yellow (construction, warmth) — callout: yellow_background, headings: yellow
- Party/Celebration: red (festive, energetic) — callout: red_background, headings: red
- Fitness Challenge: orange (motivation, energy) — callout: orange_background, headings: orange
- Default: gray (neutral, clean)

## Complexity Levels

### Simple (5-8 blocks): Quick plan
callout → heading_1 → to_do(items x3-4) → database_ref

### Medium (10-15 blocks): Standard plan with phases
callout → divider → heading_2(Phase 1) → to_do(items) → heading_2(Phase 2) → to_do(items) → divider → heading_1 → database_ref → toggle(tips)

### Complex (20-30 blocks): Full planning system
callout → quote(goal statement) → divider → column_list(D-day countdown sidebar + main plan) → heading_2(Phase 1) → to_do(items) → heading_2(Phase 2) → to_do(items) → heading_2(Phase 3) → to_do(items) → heading_2(Phase 4) → to_do(items) → divider → heading_1 → database_ref → divider → heading_2(budget summary) → numbered_list(cost breakdown) → toggle(FAQ x3) → toggle(contingency plan)

## Cross-Skill Combinations

- plan + track: "시험 계획 + 공부 기록" — Use plan for study schedule & milestones + track for daily study hours tracking
- plan + collect: "여행 계획 + 맛집/명소 수집" — Use plan for trip itinerary & packing list + collect for destination/restaurant collection
- plan + manage: "이벤트 계획 + 업무 관리" — Use plan for event timeline & checklist + manage for task assignment kanban board
- plan + hub: "프로젝트 마스터 플랜" — Use hub as project home with navigation + plan for each milestone/phase planning page
- plan + organize: "이사 계획 + 짐 정리" — Use plan for moving timeline & checklist + organize for inventory/belongings catalog

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
- Primary: blue | Accent: green | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 📅 다음 일정 (callout, green_background)
  - 🎯 진행률 (callout, green_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "완벽한 계획이 성공의 시작입니다! 하나씩 체크해보세요 📅" (blue_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with calendar view (기본), table view (체크리스트)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "minimal" (maps to themed Unsplash cover)
