---
name: goals
description: Creates goal and OKR management templates for objective setting, key results tracking, progress dashboards, and quarterly reviews. Board-driven with timeline and table views.
---

# Goals (목표 관리)

Creates templates for goal setting and progress tracking including OKRs, quarterly objectives, personal milestones, and achievement dashboards.

## Quick Start

1. **Identify goal context**: What kind of goals? (OKR, personal growth, fitness, career, annual plan)
2. **Design properties**: Always include status + number(progress%) + date(deadline). Add context-specific fields.
3. **Set layout**: Two-column (left 25% progress overview / right 75% goal board DB)
4. **Add board view**: Essential for status-based goal pipeline visualization
5. **Generate samples**: 5 goals at different progress stages with realistic key results

## Template Structure

### Layout
Two-column (left 25% progress stats / right 75% goal tracking database)

### Block Order
1. callout: Goal-setting motivational message (theme color, context icon)
2. column_list:
   - Column 1 (25%): Overall progress callout + completed goals callout
   - Column 2 (75%): Main goal tracking content area
3. divider
4. heading_1: Main title (theme color)
5. database_ref: Inline database here
6. toggle: "목표 설정 가이드" with SMART goal framework and OKR tips

### Database Design

Required properties (always include):
- title: Goal/Objective name
- status: Progress stage (설정/진행중/검토/완료/보류)
- number: Progress percentage (0-100)
- date: Deadline

Context-dependent properties (AI decides):
- rich_text: Key results (measurable outcomes)
- select: Category (업무/개인/건강/학습/재무/관계)
- select: Priority (상/중/하)
- select: Quarter (Q1/Q2/Q3/Q4)
- rich_text: Notes/reflection
- number: Target value
- number: Current value
- checkbox: Milestone reached

### Views
- Required: board (PRIMARY - goals grouped by status for pipeline view)
- Optional: table (all goals with progress numbers)
- Optional: timeline (goal deadlines and duration visualization)

### Sub-Pages
- "분기별 리뷰" (Quarterly Review): Reflection template for each quarter with achievements and learnings
- "목표 아카이브" (Goal Archive): Completed and past goals for reference and motivation
- "핵심 결과 추적" (Key Results Log): Detailed tracking of measurable outcomes per objective

### Sample Data
Generate 5 goals at different progress stages with realistic Korean goal data.
Each item needs: relevant icon, status, progress %, key results, and deadline.

## Content Adaptation Examples

**OKR Framework**: Properties → objective, key results(rich_text x3), progress%, quarter, owner, status, confidence(1-10)
**Annual Goals**: Properties → category, milestone(multi_select), progress%, deadline, reward(rich_text), reflection
**Career Goals**: Properties → skill area, current level, target level, action plan(rich_text), mentor, timeline
**Health Goals**: Properties → goal type(체중/운동/식단), target number, current number, daily action, streak count
**Financial Goals**: Properties → target amount, saved amount, monthly saving, deadline, strategy(rich_text)
**Study Goals**: Properties → subject, target score, current score, study hours/week, exam date, resources(url)

## Formatting Rules

- Callout icon should match context (🎯 general, 📈 OKR, 💪 health, 📚 study, 💰 finance)
- Board view is the PRIMARY view (status pipeline is key for goal management)
- Keep properties under 10 (goals need tracking fields but stay motivating)
- Progress number should show percentage format (0-100%)
- Quick stats callout should show key metrics (total goals, completion rate, on-track count)

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic deadline dates within current quarter and next quarter
- Status values: spread across all stages (설정, 진행중, 검토, 완료, 보류)
- Progress values: varied realistic percentages (0%, 25%, 50%, 75%, 100%)
- Category values: use different categories for variety (업무, 개인, 건강, 학습, 재무)
- Priority values: mix of 상, 중, 하
- Key results: specific measurable outcomes (월 매출 500만원 달성, 주 3회 운동, 자격증 취득, 독서 12권)
- Goal names: realistic Korean goal titles (Q2 매출 목표 달성, 체력 향상 프로그램, 영어 회화 마스터, 비상금 1000만원)

## Pro Design Guide

### Color Palette
- Primary: blue | Accent: green | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 🎯 전체 목표 (callout, green_background)
  - 📈 평균 진행률 (callout, green_background)
  - ✅ 달성 완료 (callout, green_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "목표를 세우고 매일 한 걸음씩! 꾸준함이 성취를 만듭니다 🎯" (blue_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with board view (기본, 상태별 목표), table view (상세), timeline view (일정)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "business" (maps to themed Unsplash cover)
