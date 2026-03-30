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

## Formatting Rules

- Board view is the PRIMARY view
- Status options should have logical progression
- Sample data should cover ALL statuses (show the pipeline)
- Priority colors: High=red, Medium=yellow, Low=green

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±2 weeks
- Status values: spread across all statuses (시작 전, 진행 중, 완료)
- Select values: use different options for variety
- Number values: use realistic, varied numbers
- Checkbox: mix of true and false
