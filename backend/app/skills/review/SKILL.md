---
name: review
description: 주간/월간 회고 및 목표 달성 리뷰. KPT, 4L 프레임워크로 정기적으로 돌아보는 성장 기록.
---

# Review (회고/리뷰)

Creates retrospective templates for weekly, monthly, and quarterly reviews. Structured reflection using KPT, 4L frameworks with achievement tracking and goal setting.

## Quick Start

1. **Identify review cycle**: Weekly, monthly, quarterly, or annual?
2. **Design properties**: Period + type + strengths + improvements + next goals + achievement rate
3. **Set layout**: Two-column (Review Stats sidebar 25% + main review 75%)
4. **Add gallery view**: Card-based review archive for visual browsing
5. **Generate samples**: 5 realistic review entries with Korean context

## Template Structure

### Layout
Two-column: left 25% (Review Stats + Quick Links) / right 75% (review area)

### Block Order
1. callout: Welcome message (green_background, 🔄)
2. divider
3. column_list:
   - left column:
     - heading_2: "회고 통계"
     - callout: "총 회고 수" (green_background, 📊)
     - callout: "평균 달성률" (green_background, 📈)
     - divider
     - heading_2: "프레임워크"
     - link_to_page: sub-page 1
     - link_to_page: sub-page 2
   - right column:
     - heading_1: Template title (green)
     - callout: "정기적인 회고로 성장하세요" (👇, green_background)
4. divider
5. database_ref: Inline database here
6. divider
7. toggle: 회고 작성 프레임워크
8. toggle: 자주 묻는 질문

### Database Design

Required properties (always include):
- title: 기간 (예: 2026년 4월 3주차)
- select: 유형 (주간/월간/분기/연간)
- rich_text: 잘한 점 (Keep)
- rich_text: 개선할 점 (Problem)
- rich_text: 시도할 것 (Try)
- number: 달성률 (0-100)
- date: 회고 날짜
- rich_text: 다음 목표
- select: 전체 만족도 (매우좋음/좋음/보통/아쉬움)
- checkbox: 목표 달성 여부

### Views
- Required: table (전체 회고 기록 목록)
- Optional: gallery (회고 카드 갤러리), calendar (날짜별 회고)

### Sub-Pages
Generate 2 sub-pages:
- "📋 KPT 프레임워크 가이드" — Keep/Problem/Try 작성법
- "🎯 분기별 목표 대시보드" — 90일 단위 목표 추적

### Sample Data
Generate 5 review entries spanning different periods.
Each entry: unique review type, varied achievement rates, realistic Korean reflection content.

## Content Adaptation Examples

**직장인 주간 회고**: Properties → 업무 성과, 팀 기여도, 배운 것, 다음 주 목표
**학생 월간 리뷰**: Properties → 학습 진도, 시험 결과, 과외 활동, 다음 달 계획
**프로젝트 회고**: Properties → 프로젝트명, 성공 요인, 실패 원인, 개선 사항, 팀 평가
**독서 리뷰**: Properties → 읽은 책, 핵심 인사이트, 적용 계획, 추천 점수
**운동 리뷰**: Properties → 운동 빈도, 체중 변화, 목표 대비 달성, 다음 루틴
**재정 리뷰**: Properties → 수입, 지출, 저축률, 투자 수익률, 다음 달 예산

## Formatting Rules

- Table view should be the DEFAULT view (structured review first)
- Icon should match review context (🔄📊🎯📈✍️)
- Sub-pages should have relevant icons
- Callout text should be reflective and encouraging

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within +/-2 weeks
- Select values: use different options for variety
- Number values: use realistic, varied numbers (달성률 0-100)
- Checkbox: mix of true and false

## Pro Design Guide

### Color Palette
- Primary: green | Accent: blue | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 📊 총 회고 수 (callout, blue_background)
  - 📈 평균 달성률 (callout, blue_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "돌아보는 만큼 성장합니다. 꾸준한 회고가 최고의 전략입니다 🔄" (green_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with table view (기본), gallery view (카드), calendar view (날짜별)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 회고 작성 가이드" with KPT and 4L framework explanation
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "reflection" (maps to themed Unsplash cover)
