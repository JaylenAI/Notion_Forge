---
name: hub
description: Creates dashboard and home page templates. Team home, personal workspace, project hub with navigation and overview.
---

# Hub (대시보드/홈)

Creates central hub pages with navigation sidebar, overview database, and sub-page structure. The "home base" for a team or project.

## Quick Start

1. **Identify hub purpose**: Team home? Project overview? Personal workspace?
2. **Design navigation**: What sections/sub-pages are needed?
3. **Set layout**: Two-column (sidebar 30% + main 70%)
4. **Add overview DB**: Central database with multiple views
5. **Create sub-pages**: 3-5 linked sub-pages

## Template Structure

### Layout
Two-column: left 30% (navigation sidebar) / right 70% (main content)

### Block Order
1. paragraph: Navigation bar (theme color) — "Home | Section1 | Section2 | ..."
2. divider
3. column_list:
   - left column:
     - callout: Quick tip (💡, theme color)
     - divider
     - heading_2: "Section 1" (theme color)
     - link_to_page: sub-page 1
     - link_to_page: sub-page 2
     - paragraph: (spacer)
     - heading_2: "Section 2" (theme color)
     - link_to_page: sub-page 3
     - link_to_page: sub-page 4
   - right column:
     - heading_1: Main title (theme color)
     - divider
     - callout: Action item 1 (theme color)
     - callout: Action item 2 (theme color)
     - callout: Action item 3 (theme color)
     - divider
     - callout: "Manage in database below" (👇)
4. divider
5. heading_2: Database title (theme color)
6. database_ref: Inline database here

### Database Design

Required properties:
- title: Item name
- date: Date field
- status: Status tracking
- select: Category/tag

Context-dependent:
- rich_text: Description, assignee
- select: Priority
- multi_select: Tags

### Views
- Required: calendar, board
- Optional: timeline, table

### Sub-Pages
Generate 3-5 sub-pages matching context. Each sub-page gets:
- heading_1 with icon and theme color
- callout with description
- divider

## Content Adaptation Examples

**Team home**: Sections → Team/Projects/Resources, Sub-pages → Members, Calendar, Projects, Resources
**Personal workspace**: Sections → Work/Personal/Goals, Sub-pages → Tasks, Notes, Goals, Archives
**Project hub**: Sections → Overview/Tasks/Docs, Sub-pages → Backlog, Sprint, Documentation, Meeting Notes
**School**: Sections → Classes/Study/Resources, Sub-pages → Course1, Course2, Study Plan, Materials

## Formatting Rules

- Navigation bar at top (horizontal links)
- Sidebar has section groupings with heading_2
- Sub-pages use link_to_page (not bulleted_list text)
- Main content has action callouts (button-like)
- Database below columns (not inside columns)

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±2 weeks
- Status values: spread across all statuses (시작 전, 진행 중, 완료)
- Select values: use different options for variety
- Number values: use realistic, varied numbers
- Checkbox: mix of true and false
