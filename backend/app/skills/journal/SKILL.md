---
name: journal
description: Creates journaling and reflection templates for diaries, mood tracking, gratitude logs, and weekly reviews. Text-driven with gallery view.
---

# Journal (일기/회고)

Creates templates for journaling and personal reflection including diaries, mood tracking, gratitude logs, and weekly reviews.

## Quick Start

1. **Identify journaling context**: What does the user want to reflect on? (daily diary, mood, gratitude, weekly review)
2. **Design properties**: Always include date + select(mood) + rich_text(content). Add context-specific fields.
3. **Set layout**: Single column (intimate, personal feel)
4. **Add gallery view**: Essential for card-style diary browsing
5. **Generate samples**: 5 entries with realistic Korean diary content

## Template Structure

### Layout
Single column (intimate, personal feel)

### Block Order
1. callout: Warm greeting message (theme color, context icon)
2. quote: Motivational quote (daily inspiration)
3. heading_2: Today's reflection prompt
4. to_do: Daily journaling prompts (guided questions)
5. divider
6. database_ref: Inline database here
7. toggle: "Writing tips and prompts" with instructions

### Database Design

Required properties (always include):
- title: Entry title
- date: Entry date
- select: Mood (😊좋음/😐보통/😢우울/😤화남/🤩최고)
- rich_text: Content (main journal body)

Context-dependent properties (AI decides):
- multi_select: Tags (감사/성장/도전/일상)
- number: Energy level (1-10 scale)
- checkbox: Highlight day (memorable day marker)
- select: Weather (맑음/흐림/비/눈)

### Views
- Required: gallery (PRIMARY - card-style diary layout for browsing)
- Optional: calendar (mood patterns over time)

### Sub-Pages
- "이번 달 회고" (Monthly Reflection): Summary and key takeaways for the month
- "감사 목록" (Gratitude List): Running list of things to be grateful for

### Sample Data
Generate 5 diary entries that represent a realistic two-week journal.
Each item needs: relevant icon, varied mood, filled content, and date.

## Content Adaptation Examples

**Diary**: Properties → mood, content, weather, highlight, time of day(morning/evening)
**Gratitude**: Properties → 3 things(rich_text), category(people/experience/nature/self), mood
**Mood Tracker**: Properties → mood, energy level, sleep quality, triggers(multi_select), coping strategy
**Weekly Review**: Properties → week number, wins(rich_text), challenges(rich_text), next week goals(rich_text)

## Formatting Rules

- Callout icon should match context (📝 diary, 🙏 gratitude, 💭 reflection, 📅 weekly review)
- Gallery view is the PRIMARY view (personal, visual browsing experience)
- Keep properties under 7 (journaling should feel light, not burdensome)
- Quote block should contain an inspiring or reflective message
- Sample entries should feel genuine and personal, not templated

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±2 weeks (recent diary entries)
- Mood values: spread across all mood options (not all the same)
- Content values: realistic Korean diary entries (오늘 카페에서 친구를 만났다, 새로운 프로젝트를 시작했다, etc.)
- Energy values: varied numbers between 1-10
- Tags: mix of 감사, 성장, 도전, 일상
- Checkbox: occasional highlight days marked true

## Pro Design Guide

### Color Palette
- Primary: pink | Accent: purple | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 📝 총 기록 (callout, purple_background)
  - 🌟 이번 달 기록 (callout, purple_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "오늘 하루는 어땠나요? 소중한 하루를 기록으로 남겨보세요 🌙" (pink_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with gallery view (기본, 카드형 일기장), calendar view (월별 기록)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "nature" (maps to themed Unsplash cover)
