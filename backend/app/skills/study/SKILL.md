---
name: study
description: Creates study tracking templates for learning sessions, subject progress, and exam preparation. Time-driven with calendar and table views.
---

# Study (학습/공부 기록)

Creates templates for study management including session tracking, subject progress, comprehension levels, and exam preparation schedules.

## Quick Start

1. **Identify study context**: What does the user want to track? (daily study, exam prep, subject progress, reading)
2. **Design properties**: Always include number(duration) + date + select(comprehension). Add context-specific fields.
3. **Set layout**: Two-column (left 30% stats / right 70% study log DB)
4. **Add table view**: Essential for study time analysis and filtering
5. **Generate samples**: 5+ study sessions with realistic Korean academic data

## Template Structure

### Layout
Two-column (left 30% study stats callouts / right 70% study log database)

### Block Order
1. callout: Study motivation message (theme color, context icon)
2. column_list:
   - Column 1 (30%): Today's goal callout + weekly total callout
   - Column 2 (70%): Main study log content area
3. heading_1: Main title (theme color)
4. database_ref: Inline database here
5. divider
6. toggle: "Study tips and methods" with effective study techniques

### Database Design

Required properties (always include):
- title: Study topic/subject
- number: Duration in minutes
- select: Subject (수학/영어/과학/국어/프로그래밍/자격증)
- select: Comprehension (상/중/하)
- date: Study date

Context-dependent properties (AI decides):
- rich_text: Study range/scope
- rich_text: Key takeaways/notes
- select: Method (강의/독학/문제풀이/그룹스터디)
- checkbox: Review needed
- number: Page count

### Views
- Required: table (PRIMARY - detailed study log with time totals)
- Optional: calendar (daily study overview)
- Optional: board (comprehension-based kanban)

### Sub-Pages
- "시험 일정" (Exam Schedule): Upcoming exam dates with D-day countdown and study plans
- "주간 회고" (Weekly Review): Weekly study summary and reflection notes
- "목표 설정" (Goal Setting): Monthly/quarterly study targets and progress

### Sample Data
Generate 5+ study sessions representing realistic Korean student/learner data.
Each item needs: relevant icon, filled duration, subject, comprehension level, and date.

## Content Adaptation Examples

**Exam Prep**: Properties → subject, chapter, practice score(number), target score(number), D-day(formula), weak areas(rich_text)
**Self-Study**: Properties → topic, duration, resource(rich_text), completion %(number), review date
**Reading Log**: Properties → book title, pages read(number), total pages(number), genre(select), rating(select)
**Certification**: Properties → certification name, study hours, mock test score(number), exam date, registration status(checkbox)

## Formatting Rules

- Callout icon should match context (📚 study, ✏️ exam, 📖 reading, 🎯 goal)
- Table view is the PRIMARY view (time tracking needs columns)
- Keep properties under 8 (focused on learning metrics)
- Number properties for duration should use minutes format
- Summary callouts should show today's study time and weekly total

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±1 week
- Duration values: realistic study session lengths (수학 90분, 영어 독해 45분, 프로그래밍 120분, 토익 리스닝 60분, 한국사 30분)
- Subject values: spread across different subjects
- Comprehension values: mix of 상, 중, 하
- Method values: mix of 강의, 독학, 문제풀이
- Study range: specific and realistic (미적분 Chapter 3, 토익 Part 5-6, Python 함수와 클래스)

## Pro Design Guide

### Color Palette
- Primary: blue | Accent: purple | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 📚 오늘 공부 시간 (callout, purple_background)
  - 🔥 이번 주 누적 (callout, purple_background)
  - 🎯 목표 달성률 (callout, purple_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "꾸준한 학습이 실력을 만듭니다! 오늘도 한 걸음 더 📚" (blue_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with table view (기본, 전체 학습 기록), calendar view (학습 캘린더)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "study" (maps to themed Unsplash cover)
