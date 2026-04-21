---
name: project
description: Creates project and task management templates with kanban boards, timelines, and milestone tracking. Status-driven with board and timeline views.
---

# Project (프로젝트 관리)

Creates templates for project management including task tracking, kanban boards, milestone planning, and team collaboration.

## Quick Start

1. **Identify project context**: What does the user want to manage? (tasks, milestones, team assignments, deadlines)
2. **Design properties**: Always include status + date(deadline) + select(priority). Add context-specific fields.
3. **Set layout**: Two-column (left 25% quick stats / right 75% kanban DB)
4. **Add board view**: Essential for kanban task visualization
5. **Generate samples**: 5+ tasks at different stages with realistic data

## Template Structure

### Layout
Two-column (left 25% quick stats / right 75% kanban database)

### Block Order
1. callout: Project overview message (theme color, context icon)
2. column_list:
   - Column 1 (25%): Progress summary callout + deadline callout
   - Column 2 (75%): Main kanban content area
3. divider
4. heading_1: Main title (theme color)
5. database_ref: Inline database here
6. toggle: "마일스톤 가이드" with milestone descriptions
7. toggle: "회의록 템플릿" with meeting note structure

### Database Design

Required properties (always include):
- title: Task name
- status: Progress (백로그/진행전/진행중/리뷰/완료)
- select: Priority (긴급/높음/보통/낮음)
- select: Category (기획/개발/디자인/QA/마케팅)
- date: Deadline
- rich_text: Assignee

Context-dependent properties (AI decides):
- number: Progress percentage
- multi_select: Tags/labels
- rich_text: Description/notes
- date: Start date
- select: Sprint/phase

### Views
- Required: board (PRIMARY - kanban by status)
- Optional: timeline (task duration and dependencies)
- Optional: table (all details in spreadsheet)
- Optional: calendar (deadline-based calendar)

### Sub-Pages
- "마일스톤" (Milestones): Key project milestones with target dates and deliverables
- "회의록" (Meeting Notes): Team meeting records with agenda, decisions, action items
- "리소스 & 참고자료" (Resources): Links, documents, and reference materials

### Sample Data
Generate 5+ tasks at different kanban stages with realistic Korean project data.
Each item needs: relevant icon, status, priority, category, assignee, and deadline.

## Content Adaptation Examples

**Software Project**: Properties → task, status(백로그→완료), priority, sprint(select), story points(number), assignee
**Marketing Campaign**: Properties → task, channel(SNS/블로그/광고), budget(number), deadline, status, conversion goal
**Event Planning**: Properties → task, category(장소/케이터링/홍보), budget, status, responsible person, event date
**Product Launch**: Properties → task, phase(기획/개발/테스트/출시), priority, dependency(relation), owner

## Formatting Rules

- Callout icon should match context (📋 project, ✅ task, 🎯 milestone, 👥 team)
- Board view is the PRIMARY view (kanban visualization is key)
- Keep properties under 10 (focused project tracking)
- Status options should reflect a clear workflow progression
- Quick stats callout should show key metrics (전체 태스크, 완료율, D-day)

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic deadlines within ±2 weeks
- Status values: spread across all stages (백로그, 진행전, 진행중, 리뷰, 완료)
- Priority values: mix of 긴급, 높음, 보통, 낮음
- Category values: spread across 기획, 개발, 디자인, QA
- Assignee: realistic Korean names (김민수, 이지연, 박준호, 최서영, 정우진)
- Task names: realistic project tasks (와이어프레임 설계, API 개발, QA 테스트, 런칭 페이지 제작, 사용자 인터뷰)

## Pro Design Guide

### Color Palette
- Primary: blue | Accent: orange | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (25%): stat callouts
  - 📋 전체 태스크 (callout, orange_background)
  - ✅ 완료된 태스크 (callout, orange_background)
  - 🔥 긴급 항목 (callout, orange_background)
- RIGHT (75%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "프로젝트를 체계적으로 관리하세요! 모든 태스크를 한눈에 📋" (blue_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with board view (기본, 칸반 보드), timeline view (일정), table view (상세)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "business" (maps to themed Unsplash cover)
