---
name: guide
description: Creates guide and documentation templates. Onboarding, manuals, FAQ, wiki, handover documents.
---

# Guide (안내/문서)

Creates templates for guiding others with structured documentation, checklists, and FAQ sections.

## Quick Start

1. **Identify audience**: Who is this guide for?
2. **Design sections**: Phase/step-based structure with checklists
3. **Set layout**: Single column (document flow)
4. **Add handover DB**: Track completion of guide items
5. **Include FAQ**: Toggle-based Q&A section

## Template Structure

### Layout
Single column (document-style, sequential reading)

### Block Order
1. callout: Welcome message (👋, theme color)
2. divider
3. heading_2: "Phase/Week 1" (theme color) + to_do items
4. heading_2: "Phase/Week 2" (theme color) + to_do items
5. heading_2: "Phase/Week 3" (theme color) + to_do items
6. heading_2: "Phase/Week 4" (theme color) + to_do items
7. divider
8. heading_1: "Status Tracker" (theme color)
9. database_ref: Inline database here
10. divider
11. heading_2: "FAQ" (theme color)
12. toggle: Question 1 → Answer
13. toggle: Question 2 → Answer
14. toggle: Question 3 → Answer
15. toggle: Question 4 → Answer

### Database Design

Required properties:
- title: Item/task name
- status: Progress (Not started/In progress/Done)
- rich_text: Owner/assignee
- date: Deadline

Context-dependent:
- rich_text: Notes
- select: Category/department

### Views
- Required: table (tracking progress)
- Optional: board (status overview)

### Sub-Pages
Usually none. Guide is self-contained.

### Sample Data
Generate 3-4 items showing mixed status (some done, some in progress).

## Content Adaptation Examples

**Onboarding**: Phases → Week 1-4, Properties → owner(team), deadline, status
**Manual**: Sections → Getting Started/Basic/Advanced/Troubleshooting
**FAQ**: Sections by topic with toggle Q&A
**Wiki**: Sections by department/topic, linked pages
**Handover**: Phases → Before/During/After, Properties → owner, status, deadline
**Tool Setup Guide**: Sections → Installation/Configuration/First Use/Advanced Settings, Properties → tool, version, OS, status
**Training Course**: Phases → Module 1-5 progressive learning, Properties → topic, duration, quiz score, completion
**Policy/Compliance**: Sections → Overview/Rules/Procedures/Exceptions/Contact, Properties → policy area, effective date, reviewer
**Apartment Guide (for roommates)**: Sections → House Rules/Utilities/Emergency/Neighborhood, Properties → item, responsible person, schedule
**Study Group Guide**: Sections → Schedule/Topics/Resources/Roles, Properties → week, topic, presenter, materials link

## Formatting Rules

- Welcome callout is ALWAYS first
- Phases/weeks should have clear progression
- Some checklist items pre-checked (show progress)
- FAQ toggles should have realistic Q&A
- Handover DB should show mixed statuses

## Color Theme Guide

Recommended color combinations by context:
- Onboarding/Welcome: green (fresh start, growth) — callout: green_background, headings: green
- Manual/Documentation: blue (professional, reliable) — callout: blue_background, headings: blue
- FAQ/Help Center: yellow (helpful, approachable) — callout: yellow_background, headings: yellow
- Wiki/Knowledge Base: purple (knowledge, wisdom) — callout: purple_background, headings: purple
- Handover/Transition: orange (transition, warm) — callout: orange_background, headings: orange
- Training/Course: blue (educational, focused) — callout: blue_background, headings: blue
- Policy/Compliance: red (important, formal) — callout: red_background, headings: red
- Tool Setup Guide: gray (technical, clean) — callout: gray_background, headings: gray
- Default: gray (neutral, clean)

## Complexity Levels

### Simple (5-8 blocks): Quick guide
callout → heading_1 → numbered_list(steps x3-4) → toggle(FAQ)

### Medium (10-15 blocks): Standard guide with phases
callout → divider → heading_2(Phase 1) → to_do(items) → heading_2(Phase 2) → to_do(items) → divider → heading_1(tracker) → database_ref → toggle(FAQ x2)

### Complex (20-30 blocks): Full documentation system
callout → quote(welcome motto) → divider → heading_2(Phase 1) → to_do(items) → heading_2(Phase 2) → to_do(items) → heading_2(Phase 3) → to_do(items) → heading_2(Phase 4) → to_do(items) → divider → heading_1(status tracker) → database_ref → divider → heading_2(key contacts) → bulleted_list(contact info) → heading_2(FAQ) → toggle(Q&A x5) → toggle(troubleshooting) → toggle(resource links) → toggle(feedback form)

## Cross-Skill Combinations

- guide + track: "습관 만들기 가이드 + 일일 추적" — Use guide for habit-building onboarding doc + track for daily habit tracker
- guide + manage: "신입 온보딩 + 업무 배정 관리" — Use guide for onboarding documentation & checklist + manage for task assignment board
- guide + plan: "프로젝트 매뉴얼 + 일정 계획" — Use guide for project documentation/wiki + plan for project timeline & milestones
- guide + hub: "팀 위키 + 팀 홈" — Use hub as team home dashboard + guide for each department's onboarding/manual page
- guide + collect: "요리 입문 가이드 + 레시피 모음" — Use guide for cooking basics tutorial + collect for recipe collection gallery

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
- Primary: green | Accent: blue | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 📖 총 가이드 (callout, blue_background)
  - ✅ 완료 단계 (callout, blue_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "이 가이드를 따라가면 누구나 쉽게 시작할 수 있습니다! 👋" (green_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with table view (기본, 진행 상태 추적), board view (상태별)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "study" (maps to themed Unsplash cover)
