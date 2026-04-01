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
**Startup dashboard**: Sections → Product/Marketing/Finance/Team, Sub-pages → Roadmap, Metrics, Budget, Hiring
**Community/Club**: Sections → Events/Members/Resources/Announcements, Sub-pages → Event Calendar, Member Directory, Shared Files
**Family hub**: Sections → Calendar/Chores/Budget/Memories, Sub-pages → Meal Plan, Grocery List, Family Calendar, Photo Album
**Freelancer workspace**: Sections → Clients/Projects/Invoices/Portfolio, Sub-pages → Active Projects, Client Directory, Invoice Tracker
**Creative studio**: Sections → Ideas/Projects/Inspiration/Publishing, Sub-pages → Mood Board, Work in Progress, Portfolio, Submissions
**Research lab**: Sections → Papers/Experiments/Data/Meetings, Sub-pages → Literature Review, Experiment Log, Dataset Index, Lab Notes

## Formatting Rules

- Navigation bar at top (horizontal links)
- Sidebar has section groupings with heading_2
- Sub-pages use link_to_page (not bulleted_list text)
- Main content has action callouts (button-like)
- Database below columns (not inside columns)

## Color Theme Guide

Recommended color combinations by context:
- Team Home: blue (professional, trustworthy) — callout: blue_background, headings: blue
- Personal Workspace: purple (creative, personal) — callout: purple_background, headings: purple
- Project Hub: green (progress, productive) — callout: green_background, headings: green
- School/Academic: blue (scholarly, focused) — callout: blue_background, headings: blue
- Startup/Business: orange (dynamic, ambitious) — callout: orange_background, headings: orange
- Community/Club: yellow (friendly, social) — callout: yellow_background, headings: yellow
- Family/Household: pink (warm, caring) — callout: pink_background, headings: pink
- Creative Studio: purple (artistic, imaginative) — callout: purple_background, headings: purple
- Default: gray (neutral, clean)

## Complexity Levels

### Simple (5-8 blocks): Quick hub
callout → heading_1 → link_to_page(x3) → database_ref

### Medium (10-15 blocks): Standard hub with sidebar
callout → divider → column_list(navigation sidebar + main content with action callouts) → divider → heading_2 → database_ref → toggle(usage tip)

### Complex (20-30 blocks): Full dashboard system
paragraph(nav bar) → divider → column_list(sidebar with sections/links + main content with title/action callouts/summary stats) → divider → heading_2(overview DB) → database_ref → divider → heading_2(quick links) → bulleted_list(resource links) → column_list(announcements callout + upcoming deadlines callout) → toggle(workspace guide) → toggle(FAQ x3) → toggle(customization tips)

## Cross-Skill Combinations

- hub + manage: "팀 홈 + 프로젝트 보드" — Use hub as team home dashboard + manage for project kanban boards linked as sub-pages
- hub + track: "라이프 대시보드" — Use hub as personal life dashboard + track DBs for each area (exercise, study, habits) linked from sidebar
- hub + plan: "프로젝트 마스터 플랜" — Use hub as project overview + plan pages for each milestone/release phase
- hub + collect: "취미 아카이브 허브" — Use hub as central hobby home + collect pages for each collection (books, movies, wine)
- hub + guide: "팀 위키 허브" — Use hub as team home with navigation + guide pages for onboarding, manuals, and FAQs
- hub + organize: "리소스 관리 센터" — Use hub as central resource dashboard + organize pages for contacts, bookmarks, and inventory

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±2 weeks
- Status values: spread across all statuses (시작 전, 진행 중, 완료)
- Select values: use different options for variety
- Number values: use realistic, varied numbers
- Checkbox: mix of true and false
