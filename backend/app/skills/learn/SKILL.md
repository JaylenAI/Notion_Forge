---
name: learn
description: Creates learning and study templates for courses, exam prep, language learning, and skill roadmaps. Progress-driven with table and board views.
---

# Learn (학습/공부)

Creates templates for learning management including course tracking, exam preparation, language learning, and skill development roadmaps.

## Quick Start

1. **Identify learning context**: What does the user want to study? (course, exam, language, skill)
2. **Design properties**: Always include status + date + select(category). Add context-specific fields.
3. **Set layout**: Single column (structured, curriculum-style)
4. **Add table view**: Essential for progress tracking at a glance
5. **Generate samples**: 5 items at various progress levels

## Template Structure

### Layout
Single column (structured, curriculum-style)

### Block Order
1. callout: Learning goal message (theme color, context icon)
2. heading_2: Curriculum outline
3. numbered_list: Phases/weeks of the learning plan
4. divider
5. heading_1: Main title (theme color)
6. database_ref: Inline database here
7. toggle: "Study tips and techniques" with instructions
8. toggle: "Resources and references" with useful links

### Database Design

Required properties (always include):
- title: Topic/chapter name
- status: Progress stage (시작전/학습중/복습/완료)
- date: Study date
- select: Category/subject

Context-dependent properties (AI decides):
- number: Progress percentage (0-100)
- rich_text: Notes/key takeaways
- multi_select: Tags (개념/실습/퀴즈)
- checkbox: Review needed (flagged for revisit)
- select: Difficulty (쉬움/보통/어려움)

### Views
- Required: table (PRIMARY - progress tracking with all columns visible)
- Optional: board (by status for workflow overview)

### Sub-Pages
- "학습 자료" (Study Materials): Collected resources, links, and reference materials
- "오답 노트" (Mistakes Log): Record of errors and corrections for review

### Sample Data
Generate 5 study items at various stages of progress.
Each item needs: relevant icon, status, progress percentage, study date, and notes.

## Content Adaptation Examples

**Course**: Properties → module/week, status, progress %, instructor notes, assignment due date, lecture link(url)
**Exam Prep**: Properties → subject/chapter, status, mastery level(number), practice score(number), review flag(checkbox)
**Language**: Properties → skill area(vocab/grammar/speaking/listening), level, words learned(number), practice time(number)
**Skill Roadmap**: Properties → milestone, status(beginner/intermediate/advanced), target date, completed projects(number)

## Formatting Rules

- Callout icon should match context (📚 course, 📝 exam, 🌍 language, 🎯 skill roadmap)
- Table view is the PRIMARY view (progress data needs structured columns)
- Keep properties under 8 (learning should feel manageable, not overwhelming)
- Numbered list should outline a clear learning path or curriculum
- Progress percentage should reflect realistic learning stages

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±2 weeks
- Status values: spread across all statuses (시작전, 학습중, 복습, 완료)
- Progress values: varied percentages (0%, 30%, 60%, 85%, 100%)
- Category values: use different subjects/topics for variety
- Tags: mix of 개념, 실습, 퀴즈
- Notes: realistic Korean study notes (변수와 자료형 개념 정리, 리스트 컴프리헨션 실습 완료, etc.)
- Checkbox: some items flagged for review, some not

## Pro Design Guide

### Color Palette
- Primary: blue | Accent: purple | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 📚 수강 중 (callout, purple_background)
  - ✅ 수강 완료 (callout, purple_background)
  - ⏱️ 총 학습 시간 (callout, purple_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "배움에는 끝이 없습니다! 오늘도 한 걸음 성장해보세요 📚" (blue_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with table view (기본, 진행률 추적), board view (학습 상태별)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "study" (maps to themed Unsplash cover)
