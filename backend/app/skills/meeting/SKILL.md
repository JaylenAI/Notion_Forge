---
name: meeting
description: Creates meeting management templates for agendas, minutes, action items, and attendee tracking. Calendar-driven with board and list views.
---

# Meeting (회의록 관리)

Creates templates for meeting management including scheduling, meeting minutes, action item tracking, and follow-up management.

## Quick Start

1. **Identify meeting context**: What type of meetings? (team standups, 1:1s, project reviews, all-hands)
2. **Design properties**: Always include date + select(type) + rich_text(action items). Add context-specific fields.
3. **Set layout**: Two-column (left 25% upcoming meetings / right 75% meeting DB)
4. **Add calendar view**: Essential for meeting schedule visualization
5. **Generate samples**: 5 meetings with different types, statuses, and action items

## Template Structure

### Layout
Two-column (left 25% upcoming & stats / right 75% meeting database)

### Block Order
1. callout: Meeting management intro message (theme color, context icon)
2. column_list:
   - Column 1 (25%): This week meetings callout + pending action items callout
   - Column 2 (75%): Main meeting content area
3. divider
4. heading_1: Main title (theme color)
5. database_ref: Inline database here
6. toggle: "회의 진행 가이드" with agenda template and facilitation tips

### Database Design

Required properties (always include):
- title: Meeting name/topic
- date: Meeting date & time
- select: Type (정기회의/임시회의/1:1/전체회의/프로젝트/브레인스토밍)
- rich_text: Action items

Context-dependent properties (AI decides):
- multi_select: Attendees (team member names)
- select: Status (예정/진행중/완료/취소)
- rich_text: Agenda
- rich_text: Meeting notes/minutes
- rich_text: Decisions made
- select: Priority (높음/보통/낮음)
- number: Duration (minutes)
- url: Meeting link (Zoom/Google Meet)

### Views
- Required: calendar (PRIMARY - meeting schedule overview)
- Optional: board (meetings grouped by status)
- Optional: table (all meeting details in spreadsheet)
- Optional: list (recent meetings quick scan)

### Sub-Pages
- "회의록 템플릿" (Minutes Template): Standard meeting minutes structure with agenda, decisions, and action items
- "액션아이템 추적" (Action Item Tracker): Follow-up task list from all meetings
- "정기회의 안건" (Recurring Agenda): Standing agenda items for regular meetings

### Sample Data
Generate 5 meetings with different types and realistic Korean business data.
Each item needs: relevant icon, meeting type, attendees, action items, and status.

## Content Adaptation Examples

**Team Standup**: Properties → date, blocker(checkbox), yesterday done(rich_text), today plan(rich_text), duration(15min fixed)
**1:1 Meeting**: Properties → manager, report, mood(select), career topic(rich_text), feedback(rich_text), next meeting date
**Project Review**: Properties → project name, milestone, progress(number%), demo ready(checkbox), blockers, decisions
**All-Hands**: Properties → presenter, department, announcements(rich_text), Q&A notes, recording link(url)
**Client Meeting**: Properties → client company, contact person, proposal status, follow-up date, deal value

## Formatting Rules

- Callout icon should match context (📋 general, 🤝 1:1, 📊 review, 💡 brainstorm)
- Calendar view is the PRIMARY view (scheduling is key for meetings)
- Keep properties under 10 (meetings need detail but stay scannable)
- Status options should reflect meeting lifecycle (예정 → 진행중 → 완료)
- Quick stats callout should show key metrics (this week meetings, pending actions, completed)

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic meeting dates within ±1 week
- Type values: spread across meeting types (정기회의, 임시회의, 1:1, 전체회의, 프로젝트)
- Status values: mix of 예정, 진행중, 완료
- Attendees: realistic Korean business names (김대리, 이팀장, 박매니저, 최부장, 정사원)
- Action items: specific, actionable Korean tasks (디자인 시안 검토, API 문서 업데이트, 고객사 미팅 일정 조율)
- Meeting names: realistic Korean meeting titles (주간 스탠드업, Q2 성과 리뷰, 신규 프로젝트 킥오프, 디자인 스프린트)
- Duration: realistic durations (15분, 30분, 45분, 60분, 90분)

## Pro Design Guide

### Color Palette
- Primary: blue | Accent: green | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 📅 이번 주 회의 (callout, green_background)
  - ✅ 완료된 액션아이템 (callout, green_background)
  - ⏳ 대기 중 액션아이템 (callout, green_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "효율적인 회의, 확실한 후속 조치! 모든 회의를 기록하세요 📋" (blue_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with calendar view (기본, 회의 일정), board view (상태별), table view (상세)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "business" (maps to themed Unsplash cover)
