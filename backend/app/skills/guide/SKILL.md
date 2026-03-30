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

## Formatting Rules

- Welcome callout is ALWAYS first
- Phases/weeks should have clear progression
- Some checklist items pre-checked (show progress)
- FAQ toggles should have realistic Q&A
- Handover DB should show mixed statuses

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±2 weeks
- Status values: spread across all statuses (시작 전, 진행 중, 완료)
- Select values: use different options for variety
- Number values: use realistic, varied numbers
- Checkbox: mix of true and false
