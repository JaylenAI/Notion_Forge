---
name: manage
description: Creates process management templates with status tracking. Projects, hiring, sales pipelines, bug tracking, sprint boards.
---

# Manage (관리/프로세스)

Creates templates for managing processes with status-based tracking. Kanban board view is central.

## Quick Start

1. **Identify process**: What workflow is being managed?
2. **Design properties**: Title + status + assignee + due date + priority
3. **Set layout**: Single column (process-focused)
4. **Add board view**: Kanban is essential for status management
5. **Generate samples**: 5 items across different statuses

## Template Structure

### Layout
Single column (clean, board-focused)

### Block Order
1. callout: Process description (theme color, context icon)
2. divider
3. heading_1: Board title (theme color)
4. database_ref: Inline database here
5. divider
6. toggle: "How to use"
7. toggle: "Status guide" (explain each status)

### Database Design

Required properties:
- title: Task/item name
- status: Process stages (AI defines based on context)
- rich_text: Assignee/owner
- date: Due date/deadline

Context-dependent:
- select: Priority (High/Medium/Low)
- select: Category/type
- number: Score, points, budget
- date: Start date (for timeline view)

### Views
- Required: board (kanban, grouped by status)
- Optional: timeline (if date ranges exist), table (detail view)

### Sub-Pages
Usually none. Management templates are self-contained.

### Sample Data
Generate 5 items spread across ALL statuses (not all "not started").

## Content Adaptation Examples

**Project**: Status → Not started/In progress/Done, Properties → sprint, story points, category(FE/BE/QA)
**Hiring**: Status → Applied/Screening/Interview/Offer/Hired, Properties → position, department, interviewer
**Sales**: Status → Lead/Meeting/Proposal/Contract, Properties → company, deal size, contact
**Bug tracking**: Status → Open/In progress/Fixed/Closed, Properties → severity, component, reporter
**Content pipeline**: Status → Idea/Draft/Review/Published, Properties → type, author, publish date
**Customer support**: Status → New/Assigned/In progress/Resolved/Closed, Properties → priority, category, assignee, SLA deadline
**Event management**: Status → Planning/Confirmed/In progress/Completed, Properties → event type, venue, budget, attendees
**Inventory orders**: Status → Requested/Approved/Ordered/Shipped/Received, Properties → item, quantity, supplier, cost
**Sprint board**: Status → Backlog/To do/In progress/Review/Done, Properties → story points, assignee, epic, sprint number
**Partnership pipeline**: Status → Outreach/Negotiation/Agreement/Active, Properties → partner company, contact, deal value, renewal date

## Formatting Rules

- Board view is the PRIMARY view
- Status options should have logical progression
- Sample data should cover ALL statuses (show the pipeline)
- Priority colors: High=red, Medium=yellow, Low=green

## Color Theme Guide

Recommended color combinations by context:
- Project Management: blue (professional, structured) — callout: blue_background, headings: blue
- Hiring/Recruitment: purple (people-focused, growth) — callout: purple_background, headings: purple
- Sales Pipeline: green (money, success) — callout: green_background, headings: green
- Bug Tracking: red (urgent, attention) — callout: red_background, headings: red
- Content Pipeline: orange (creative, productive) — callout: orange_background, headings: orange
- Sprint/Agile: blue (tech, systematic) — callout: blue_background, headings: blue
- Customer Support: yellow (approachable, helpful) — callout: yellow_background, headings: yellow
- Event Management: pink (festive, organized) — callout: pink_background, headings: pink
- Default: gray (neutral, clean)

## Complexity Levels

### Simple (5-8 blocks): Quick board
callout → heading_1 → database_ref → toggle(status guide)

### Medium (10-15 blocks): Standard management board
callout → divider → heading_2(overview) → paragraph(description) → heading_1 → database_ref → divider → toggle(how to use) → toggle(status guide) → toggle(FAQ)

### Complex (20-30 blocks): Full management system
callout → quote(team motto) → divider → column_list(KPI stats sidebar + main board) → heading_1 → database_ref → divider → heading_2(process guide) → numbered_list(workflow steps) → heading_2(status definitions) → bulleted_list(status descriptions) → to_do(weekly review checklist) → toggle(escalation policy) → toggle(FAQ x3) → toggle(retrospective template)

## Cross-Skill Combinations

- manage + track: "팀 프로젝트 + 개인 업무 기록" — Use manage for project kanban board + track for individual daily task completion log
- manage + plan: "제품 출시 관리 + 출시 계획" — Use manage for feature pipeline board + plan for launch timeline & checklist
- manage + hub: "팀 홈 + 프로젝트 보드" — Use hub as team dashboard with navigation + manage for each project's kanban board
- manage + guide: "신입 온보딩 + 업무 배정" — Use guide for onboarding documentation + manage for task assignment & status tracking
- manage + organize: "고객 관리 + 거래처 정리" — Use manage for sales pipeline + organize for customer/contact directory

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
- Primary: blue | Accent: orange | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 📋 진행 중 작업 (callout, orange_background)
  - ✅ 이번 주 완료 (callout, orange_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "체계적인 업무 관리로 생산성을 높여보세요! 📋" (blue_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with board view (기본, 상태별 칸반), table view (상세)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "business" (maps to themed Unsplash cover)
