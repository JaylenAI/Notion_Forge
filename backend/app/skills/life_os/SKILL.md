---
name: life_os
description: 라이프 OS 개인 대시보드 및 영역별 목표 관리. 건강, 관계, 재정, 커리어, 자기계발을 통합 관리.
---

# Life OS (라이프 OS/인생 관리)

Creates personal life management dashboards with area-based goal tracking. Integrates health, relationships, finance, career, and personal growth into one system.

## Quick Start

1. **Identify life areas**: Which domains does the user want to track?
2. **Design properties**: Area + category + goal + progress + next action + status
3. **Set layout**: Two-column (Life Score sidebar 25% + main dashboard 75%)
4. **Add gallery view**: Card-based area overview is essential
5. **Generate samples**: 6 realistic life areas with Korean context

## Template Structure

### Layout
Two-column: left 25% (Life Score + Quick Links) / right 75% (dashboard area)

### Block Order
1. callout: Welcome message (purple_background, 🌟)
2. divider
3. column_list:
   - left column:
     - heading_2: "Life Score"
     - callout: "전체 진행률" (purple_background, 📊)
     - callout: "이번 주 포커스" (purple_background, 🎯)
     - divider
     - heading_2: "바로가기"
     - link_to_page: sub-page 1
     - link_to_page: sub-page 2
   - right column:
     - heading_1: Template title (purple)
     - callout: "나의 인생을 디자인하세요" (👇, purple_background)
4. divider
5. database_ref: Inline database here
6. divider
7. toggle: 영역별 목표 설정 가이드
8. toggle: 주간 리뷰 체크리스트

### Database Design

Required properties (always include):
- title: 영역명
- select: 카테고리 (건강/관계/재정/커리어/자기계발/취미)
- rich_text: 현재 목표
- number: 진행률 (0-100)
- rich_text: 다음 행동
- status: 상태 (시작 전/진행 중/완료)
- date: 목표 마감일
- rich_text: 메모
- select: 우선순위 (높음/중간/낮음)
- checkbox: 이번 주 포커스

### Views
- Required: gallery (영역별 카드 갤러리)
- Optional: table (전체 목록 및 진행률), board (상태별 보드)

### Sub-Pages
Generate 2 sub-pages:
- "📅 주간 리뷰 템플릿" — 매주 돌아보는 리뷰 시트
- "🎯 분기별 목표 설정" — 90일 단위 목표 계획

### Sample Data
Generate 6 items covering all life areas.
Each item: unique icon, varied categories, different progress levels.

## Content Adaptation Examples

**미니멀리스트**: Areas → 소유물 정리, 디지털 미니멀, 시간 관리, 마인드풀니스
**직장인**: Areas → 업무 성과, 자기계발, 건강(운동/식단), 재테크, 인간관계
**대학생**: Areas → 학점, 취업 준비, 동아리, 건강, 재정(용돈 관리)
**프리랜서**: Areas → 프로젝트, 수입 관리, 스킬업, 네트워킹, 워라밸
**부모**: Areas → 육아, 가계 재정, 자기시간, 부부관계, 건강
**은퇴 준비**: Areas → 재정 계획, 건강 관리, 취미 개발, 사회 활동, 버킷리스트

## Formatting Rules

- Gallery view should be the DEFAULT view (visual overview first)
- Icon should match life context (🌟🧬💰🎯🧘)
- Sub-pages should have relevant icons
- Callout text should be motivational and warm

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within +/-2 weeks
- Status values: spread across all statuses (시작 전, 진행 중, 완료)
- Select values: use different options for variety
- Number values: use realistic, varied numbers (progress 0-100)
- Checkbox: mix of true and false

## Pro Design Guide

### Color Palette
- Primary: purple | Accent: blue | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 🌟 전체 진행률 (callout, blue_background)
  - 🎯 포커스 영역 (callout, blue_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "나의 인생을 한눈에! 모든 영역을 균형있게 성장시키세요 🌟" (purple_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with gallery view (기본), table view (상세), board view (상태별)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 Life OS 활용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "lifestyle" (maps to themed Unsplash cover)
