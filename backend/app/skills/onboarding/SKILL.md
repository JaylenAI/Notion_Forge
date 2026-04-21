---
name: onboarding
description: Creates onboarding guide templates for new hire checklists, department introductions, and training schedules. Checklist-driven with board and table views.
---

# Onboarding (온보딩/신입 가이드)

Creates templates for employee onboarding including task checklists, department introductions, IT setup guides, and training schedules.

## Quick Start

1. **Identify onboarding context**: What does the user need? (new hire checklist, department guide, training plan, IT setup)
2. **Design properties**: Always include checkbox(completion) + select(category) + date(deadline). Add context-specific fields.
3. **Set layout**: Two-column (left 30% progress stats / right 70% checklist DB)
4. **Add board view**: Essential for category-based task grouping
5. **Generate samples**: 8+ onboarding tasks across different categories

## Template Structure

### Layout
Two-column (left 30% onboarding progress callouts / right 70% checklist database)

### Block Order
1. callout: Welcome message for new hire (theme color, context icon)
2. column_list:
   - Column 1 (30%): Progress overview callout + key contacts callout
   - Column 2 (70%): Main checklist content area
3. heading_1: Main title (theme color)
4. database_ref: Inline database here
5. divider
6. toggle: "Department guide" with team introductions

### Database Design

Required properties (always include):
- title: Task name
- select: Category (IT설정/조직소개/업무교육/복리후생/행정처리)
- rich_text: Responsible person
- date: Deadline
- checkbox: Completed
- select: Priority (필수/권장/선택)

Context-dependent properties (AI decides):
- rich_text: Notes/instructions
- select: Day (Day 1/Day 2/Day 3/첫째 주/둘째 주)
- url: Reference link
- rich_text: Department

### Views
- Required: table (PRIMARY - full checklist with completion status)
- Optional: board (category-based task grouping)

### Sub-Pages
- "부서별 안내" (Department Guide): Team structure, key contacts, and role descriptions
- "IT 설정 가이드" (IT Setup Guide): Step-by-step account and tool setup instructions
- "복리후생 안내" (Benefits Guide): Company benefits, policies, and how to apply

### Sample Data
Generate 8+ onboarding tasks covering all categories with realistic corporate data.
Each item needs: relevant icon, category, responsible person, deadline, and completion status.

## Content Adaptation Examples

**New Hire Checklist**: Properties → task, category, day(Day 1-5), owner, completed, notes, priority(필수/권장)
**Training Schedule**: Properties → training topic, trainer, date, duration(number), location, materials link(url)
**IT Setup**: Properties → tool/account name, setup steps(rich_text), admin contact, completed, access level(select)
**Manager Guide**: Properties → action item, new hire name, timeline(select), status(대기/진행/완료), feedback notes

## Formatting Rules

- Callout icon should match context (🎉 welcome, ✅ checklist, 🏢 department, 💻 IT setup)
- Table view is the PRIMARY view (checklist completion tracking)
- Keep properties under 8 (clear and actionable for new hires)
- Checkbox property is essential for progress tracking
- Summary callouts should show total tasks, completed count, and remaining items

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 8 sample items per database (onboarding has many tasks)
- ALL property values must be filled (not just title and icon)
- Date values: use sequential dates from Day 1 to Week 2
- Task names: realistic Korean onboarding tasks (노트북 수령, 이메일 계정 생성, 사내 메신저 설치, 팀 소개 미팅, 사내 시스템 교육, 보안 서약서 제출, 복리후생 안내 수강, 멘토 배정)
- Category values: spread across IT설정, 조직소개, 업무교육, 복리후생, 행정처리
- Completed values: first few days completed(true), later tasks pending(false)
- Responsible: realistic Korean corporate roles (IT팀 김주임, 인사팀 박대리, 팀장님, 멘토 이선배, 총무팀 최주임)
- Priority: mix of 필수 and 권장

## Pro Design Guide

### Color Palette
- Primary: blue | Accent: green | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - ✅ 완료한 항목 (callout, green_background)
  - 📋 남은 항목 (callout, green_background)
  - 📅 예상 완료일 (callout, green_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "환영합니다! 새로운 시작을 체계적으로 준비하세요 🎉" (blue_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with table view (기본, 온보딩 체크리스트), board view (카테고리별)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "office" (maps to themed Unsplash cover)
