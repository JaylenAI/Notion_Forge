---
name: language
description: Creates language learning templates for vocabulary management, proficiency tracking, and spaced repetition review. Card-driven with gallery and board views.
---

# Language (외국어 학습)

Creates templates for foreign language learning including vocabulary cards, proficiency-based review, example sentences, and spaced repetition scheduling.

## Quick Start

1. **Identify language context**: What does the user want to learn? (vocabulary, grammar, conversation, TOEIC/JLPT)
2. **Design properties**: Always include rich_text(meaning) + select(proficiency) + date(review). Add context-specific fields.
3. **Set layout**: Two-column (left 30% progress stats / right 70% vocabulary DB)
4. **Add gallery view**: Essential for flashcard-style vocabulary review
5. **Generate samples**: 5+ vocabulary items with realistic language learning data

## Template Structure

### Layout
Two-column (left 30% learning stats callouts / right 70% vocabulary database)

### Block Order
1. callout: Language learning motivation message (theme color, context icon)
2. column_list:
   - Column 1 (30%): Words learned callout + review due callout
   - Column 2 (70%): Main vocabulary content area
3. heading_1: Main title (theme color)
4. database_ref: Inline database here
5. divider
6. toggle: "Review schedule guide" with spaced repetition explanation

### Database Design

Required properties (always include):
- title: Word/expression
- rich_text: Meaning/definition
- rich_text: Example sentence
- select: Proficiency (학습중/복습/숙달)
- date: Next review date

Context-dependent properties (AI decides):
- select: Part of speech (명사/동사/형용사/부사/표현)
- select: Level (초급/중급/고급)
- rich_text: Pronunciation/reading
- select: Source (교재/드라마/뉴스/회화)
- checkbox: Favorite/important

### Views
- Required: gallery (PRIMARY - flashcard-style vocabulary cards)
- Optional: board (proficiency-based kanban for review flow)
- Optional: table (full vocabulary list with search/filter)

### Sub-Pages
- "복습 스케줄" (Review Schedule): Spaced repetition intervals and review calendar
- "문법 노트" (Grammar Notes): Key grammar patterns organized by level
- "표현 모음" (Expression Collection): Useful phrases grouped by situation

### Sample Data
Generate 5+ vocabulary items representing realistic foreign language study.
Each item needs: relevant icon, meaning, example sentence, proficiency level, and review date.

## Content Adaptation Examples

**English Vocabulary**: Properties → word, meaning(Korean), example sentence, proficiency, part of speech, TOEIC frequency(select)
**Japanese Study**: Properties → word(kanji), reading(hiragana), meaning, JLPT level(N5-N1), example sentence, review date
**Conversation Practice**: Properties → expression, situation(select), formality(casual/formal), response example, audio link(url)
**Grammar Patterns**: Properties → pattern name, explanation(rich_text), example 1, example 2, level(초급/중급/고급), mistakes to avoid

## Formatting Rules

- Callout icon should match context (🌍 language, 📝 vocabulary, 🗣️ conversation, 📖 grammar)
- Gallery view is the PRIMARY view (flashcard-style learning)
- Keep properties under 8 (focused on memorization essentials)
- Example sentences should be practical and commonly used
- Summary callouts should show total words, mastered count, and review due count

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic review dates within ±1 week (spaced repetition intervals)
- Word values: realistic vocabulary (serendipity, ephemeral, 一期一会, 食べ放題, ambiance)
- Meaning values: clear Korean translations (우연한 발견, 덧없는, 일기일회, 무한리필, 분위기)
- Example sentences: natural and practical usage
- Proficiency values: spread across 학습중, 복습, 숙달
- Level values: mix of 초급, 중급, 고급
- Part of speech: variety of 명사, 동사, 형용사, 표현

## Pro Design Guide

### Color Palette
- Primary: blue | Accent: green | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 📝 총 단어 수 (callout, green_background)
  - ✅ 숙달 완료 (callout, green_background)
  - 🔄 오늘 복습 예정 (callout, green_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "매일 5단어, 언어의 세계가 넓어집니다! 꾸준함이 실력입니다 🌍" (blue_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with gallery view (기본, 단어 카드), board view (숙달도별), table view (전체 목록)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "study" (maps to themed Unsplash cover)
