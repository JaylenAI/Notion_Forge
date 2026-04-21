---
name: diary
description: 일기 및 하루 기록 트래커. 매일의 기분, 날씨, 감정을 기록하고 돌아보는 나만의 다이어리.
---

# Diary (일기/다이어리)

Creates daily journal templates for recording moods, weather, and daily reflections. Personal diary with emotion tracking and calendar-based browsing.

## Quick Start

1. **Identify journal style**: What does the user want to record daily?
2. **Design properties**: Title + date + mood + weather + content + gratitude
3. **Set layout**: Two-column (Today sidebar 25% + main diary 75%)
4. **Add calendar view**: Date-based browsing is essential for diaries
5. **Generate samples**: 5 realistic diary entries with Korean context

## Template Structure

### Layout
Two-column: left 25% (Today's Entry + Quick Links) / right 75% (diary area)

### Block Order
1. callout: Welcome message (pink_background, 📔)
2. divider
3. column_list:
   - left column:
     - heading_2: "오늘의 기록"
     - callout: "새 일기 쓰기" (pink_background, ✏️)
     - callout: "이번 주 돌아보기" (pink_background, 📅)
     - divider
     - heading_2: "바로가기"
     - link_to_page: sub-page 1
     - link_to_page: sub-page 2
   - right column:
     - heading_1: Template title (pink)
     - callout: "오늘 하루를 기록해보세요" (👇, pink_background)
4. divider
5. database_ref: Inline database here
6. divider
7. toggle: 일기 작성 팁
8. toggle: 자주 묻는 질문

### Database Design

Required properties (always include):
- title: 제목
- date: 날짜
- select: 기분 (최고/좋음/보통/나쁨/최악)
- select: 날씨 (맑음/흐림/비/눈/바람)
- rich_text: 오늘의 한 줄
- rich_text: 감사한 것
- rich_text: 내용
- checkbox: 운동 여부
- number: 수면 시간
- select: 에너지 (높음/보통/낮음)

### Views
- Required: calendar (날짜별 일기 캘린더)
- Optional: gallery (일기 카드 갤러리), table (전체 목록)

### Sub-Pages
Generate 2 sub-pages:
- "📊 월간 감정 리포트" — 한 달간 기분 변화 분석
- "✨ 베스트 모먼트" — 특별했던 날 모아보기

### Sample Data
Generate 5 diary entries spanning recent dates.
Each entry: unique mood, varied weather, realistic Korean daily life content.

## Content Adaptation Examples

**직장인 일기**: Properties → 업무 만족도, 퇴근 시간, 오늘의 성과, 내일 할 일
**학생 일기**: Properties → 공부 시간, 배운 것, 학교 생활, 내일 준비물
**육아 일기**: Properties → 아이 컨디션, 수유/식사, 낮잠, 발달 기록
**운동 일기**: Properties → 운동 종류, 시간, 컨디션, 체중, 식단 메모
**감정 일기**: Properties → 주요 감정, 트리거, 대처 방법, 감정 강도(1-10)
**여행 일기**: Properties → 방문지, 교통편, 경비, 오늘의 하이라이트

## Formatting Rules

- Calendar view should be the DEFAULT view (date browsing first)
- Icon should match diary context (📔✏️📝🌙💭)
- Sub-pages should have relevant icons
- Callout text should be warm and comforting

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within +/-2 weeks
- Status values: spread across all statuses (시작 전, 진행 중, 완료)
- Select values: use different options for variety
- Number values: use realistic, varied numbers
- Checkbox: mix of true and false

## Pro Design Guide

### Color Palette
- Primary: pink | Accent: purple | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 📔 총 기록 (callout, purple_background)
  - 😊 이번 주 기분 (callout, purple_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "오늘 하루도 소중한 기록으로 남겨보세요 📔" (pink_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with calendar view (기본), gallery view (카드), table view (목록)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 일기 작성 가이드" with writing tips and prompts
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "journal" (maps to themed Unsplash cover)
