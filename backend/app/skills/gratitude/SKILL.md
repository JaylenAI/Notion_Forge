---
name: gratitude
description: 감사 일기 및 긍정 기록. 매일 감사한 순간을 기록하고 행복을 쌓아가는 마음 일기.
---

# Gratitude (감사 일기)

Creates gratitude journal templates for recording daily thankfulness. Builds a positive mindset through consistent gratitude practice with category-based tracking.

## Quick Start

1. **Identify gratitude style**: What aspects of life does the user appreciate?
2. **Design properties**: Title + date + category + mood + content
3. **Set layout**: Two-column (Gratitude Stats sidebar 25% + main journal 75%)
4. **Add gallery view**: Card-based visual browsing for warm feeling
5. **Generate samples**: 5 realistic gratitude entries with Korean context

## Template Structure

### Layout
Two-column: left 25% (Gratitude Count + Quick Links) / right 75% (journal area)

### Block Order
1. callout: Welcome message (yellow_background, 🙏)
2. divider
3. column_list:
   - left column:
     - heading_2: "감사 카운터"
     - callout: "총 감사 기록" (yellow_background, 📊)
     - callout: "연속 기록일" (yellow_background, 🔥)
     - divider
     - heading_2: "바로가기"
     - link_to_page: sub-page 1
     - link_to_page: sub-page 2
   - right column:
     - heading_1: Template title (yellow)
     - callout: "오늘 감사한 일을 적어보세요" (👇, yellow_background)
4. divider
5. database_ref: Inline database here
6. divider
7. toggle: 감사 습관 가이드
8. toggle: 자주 묻는 질문

### Database Design

Required properties (always include):
- title: 감사 제목
- date: 날짜
- select: 카테고리 (사람/경험/자연/성장/일상/건강)
- select: 기분 (감사/행복/평화/따뜻/감동)
- rich_text: 상세 내용
- rich_text: 누구에게 감사한가
- checkbox: 직접 감사 표현함
- number: 감사 강도 (1-5)
- select: 시간대 (아침/오후/저녁)
- rich_text: 한 줄 요약

### Views
- Required: gallery (감사 카드 갤러리)
- Optional: calendar (날짜별 감사 기록), table (전체 목록)

### Sub-Pages
Generate 2 sub-pages:
- "💌 감사 편지 모음" — 소중한 사람에게 쓴 감사 편지
- "🌈 베스트 감사 순간" — 특별히 감동적이었던 순간 모음

### Sample Data
Generate 5 gratitude entries spanning recent dates.
Each entry: unique category, varied moods, realistic Korean daily gratitude content.

## Content Adaptation Examples

**직장인**: Gratitude → 동료의 도움, 성장 기회, 맛있는 점심, 퇴근 후 여유
**학생**: Gratitude → 친구와의 대화, 좋은 수업, 부모님 응원, 맛집 발견
**부모**: Gratitude → 아이의 첫 걸음, 배우자의 배려, 가족 식사, 건강한 하루
**시니어**: Gratitude → 건강한 아침, 오랜 친구, 산책길 풍경, 손주의 전화
**커플**: Gratitude → 파트너의 관심, 함께한 식사, 공유한 취미, 서로의 성장

## Formatting Rules

- Gallery view should be the DEFAULT view (warm visual first)
- Icon should match gratitude context (🙏💛✨🌻🌈)
- Sub-pages should have relevant icons
- Callout text should be warm and uplifting

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within +/-2 weeks
- Select values: use different options for variety
- Number values: use realistic, varied numbers (감사 강도 1-5)
- Checkbox: mix of true and false

## Pro Design Guide

### Color Palette
- Primary: yellow | Accent: orange | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 🙏 총 감사 기록 (callout, orange_background)
  - 🔥 연속 기록일 (callout, orange_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "감사는 행복의 시작입니다. 오늘도 감사한 순간을 기록하세요 🙏" (yellow_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with gallery view (기본), calendar view (날짜별), table view (목록)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 감사 습관 만들기" with tips for daily gratitude practice
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "nature" (maps to themed Unsplash cover)
