---
name: sprint
description: Creates agile sprint management templates for user stories, sprint planning, velocity tracking, and retrospectives. Status-driven with board and table views.
---

# Sprint (스프린트/애자일)

Creates templates for agile sprint management including user story tracking, sprint planning, velocity analysis, and team retrospectives.

## Quick Start

1. **Identify sprint context**: What does the user want to manage? (stories, sprint planning, velocity, retrospective)
2. **Design properties**: Always include status + number(points) + select(sprint). Add context-specific fields.
3. **Set layout**: Two-column (left 25% sprint stats / right 75% story board)
4. **Add board view**: Essential for sprint kanban visualization
5. **Generate samples**: 5+ stories at different stages with realistic data

## Template Structure

### Layout
Two-column (left 25% sprint stats / right 75% story board)

### Block Order
1. callout: Sprint goal message (theme color, context icon)
2. column_list:
   - Column 1 (25%): Sprint velocity callout + burndown callout + remaining points callout
   - Column 2 (75%): Main kanban content area
3. divider
4. heading_1: Main title (theme color)
5. database_ref: Inline database here
6. toggle: "번다운 차트 가이드" with burndown tracking tips
7. toggle: "스프린트 회고" with retrospective template

### Database Design

Required properties (always include):
- title: Story/task name
- status: Stage (백로그/할일/진행중/코드리뷰/QA/완료)
- number: Story points (1/2/3/5/8/13)
- select: Sprint (Sprint 1/Sprint 2/Sprint 3/Sprint 4)
- select: Epic (인증/결제/대시보드/알림/설정)
- rich_text: Assignee

Context-dependent properties (AI decides):
- select: Type (기능/버그/기술부채/리서치)
- select: Priority (P0/P1/P2/P3)
- rich_text: Acceptance criteria
- date: Due date
- checkbox: Blocked

### Views
- Required: board (PRIMARY - sprint kanban by status)
- Optional: table (all stories with point totals per sprint)
- Optional: board (grouped by epic for backlog grooming)

### Sub-Pages
- "스프린트 회고" (Sprint Retrospective): Keep/Problem/Try format with action items
- "백로그 관리" (Backlog Grooming): Prioritized list of upcoming stories and epics
- "팀 약속" (Team Agreements): Definition of Done, working agreements, code review rules

### Sample Data
Generate 5+ user stories at different sprint stages with realistic Korean dev team data.
Each item needs: relevant icon, status, story points, sprint, epic, and assignee.

## Content Adaptation Examples

**Software Sprint**: Properties → story, status(백로그→완료), points, sprint, epic, assignee, type(기능/버그)
**Design Sprint**: Properties → task, phase(이해/정의/발산/결정/검증), owner, deliverable, feedback(rich_text)
**Product Sprint**: Properties → feature, priority(P0-P3), effort(number), impact(select), requester, release version
**Data Sprint**: Properties → task, pipeline stage, dataset(select), owner, ETA, dependencies(rich_text)

## Formatting Rules

- Callout icon should match context (🏃 sprint, 📋 backlog, 🔄 iteration, 📊 velocity)
- Board view is the PRIMARY view (kanban is core to sprint workflow)
- Keep properties under 10 (agile values simplicity)
- Story points should use Fibonacci sequence (1, 2, 3, 5, 8, 13)
- Quick stats callout should show sprint metrics (총 포인트, 완료 포인트, 남은 일수)

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Status values: spread across 백로그, 할일, 진행중, 코드리뷰, QA, 완료
- Story points: use Fibonacci (1, 2, 3, 5, 8) with realistic distribution
- Sprint: items should be in Sprint 1 or Sprint 2
- Epic values: spread across realistic epics (인증, 결제, 대시보드, 알림)
- Assignee: realistic Korean developer names (김개발, 이프론트, 박백엔드, 최디자인, 정QA)
- Story names: realistic dev tasks (소셜 로그인 구현, 결제 API 연동, 대시보드 차트 추가, 푸시 알림 설정, 회원가입 유효성 검사)

## Pro Design Guide

### Color Palette
- Primary: blue | Accent: orange | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (25%): stat callouts
  - 🏃 스프린트 목표 (callout, orange_background)
  - 📊 총 포인트 (callout, orange_background)
  - ✅ 완료 포인트 (callout, orange_background)
- RIGHT (75%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "스프린트 목표를 달성하세요! 팀의 진행 상황을 한눈에 🏃" (blue_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with board view (기본, 스프린트 칸반), table view (전체 스토리)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "tech" (maps to themed Unsplash cover)
