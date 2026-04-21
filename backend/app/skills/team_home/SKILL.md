---
name: team_home
description: 팀 홈 대시보드 및 공지/일정 관리. 팀 공지사항, 주요 링크, 목표 추적, 일정 관리를 한 곳에서.
---

# Team Home (팀 홈/대시보드)

Creates team dashboard templates with announcements, schedules, goals, and quick links. Central hub for team collaboration and information sharing.

## Quick Start

1. **Identify team context**: What team/department is this for?
2. **Design properties**: Title + type(공지/링크/목표/일정) + assignee + deadline + priority + status
3. **Set layout**: Two-column (Quick Action sidebar 25% + main dashboard 75%)
4. **Add board view**: Status-based kanban for task overview
5. **Generate samples**: 5 realistic team items (Korean company context)

## Template Structure

### Layout
Two-column: left 25% (Quick Action + Team Links) / right 75% (dashboard area)

### Block Order
1. callout: Welcome message (blue_background, 🏠)
2. divider
3. column_list:
   - left column:
     - heading_2: "Quick Action"
     - callout: "새 공지 등록" (blue_background, 📢)
     - callout: "회의록 작성" (blue_background, 📝)
     - divider
     - heading_2: "팀 링크"
     - link_to_page: sub-page 1
     - link_to_page: sub-page 2
   - right column:
     - heading_1: Template title (blue)
     - callout: "팀 현황을 한눈에 확인하세요" (👇, blue_background)
4. divider
5. database_ref: Inline database here
6. divider
7. toggle: 팀 규칙 및 가이드
8. toggle: 자주 묻는 질문

### Database Design

Required properties (always include):
- title: 항목명
- select: 유형 (공지/링크/목표/일정)
- rich_text: 담당자
- date: 마감일
- select: 중요도 (높음/중간/낮음)
- status: 상태 (시작 전/진행 중/완료)
- rich_text: 메모
- checkbox: 고정

### Views
- Required: table (전체 항목 목록 및 필터)
- Optional: board (상태별 칸반), calendar (일정 및 마감일)

### Sub-Pages
Generate 2 sub-pages:
- "📋 회의록 아카이브" — 팀 회의 기록 모음
- "📚 팀 위키" — 팀 규칙, 온보딩, 참고 자료

### Sample Data
Generate 5 items with realistic Korean company context.
Each item: unique icon, varied types, different priorities and statuses.

## Content Adaptation Examples

**개발팀**: Properties → 스프린트, 담당 개발자, PR 링크, 배포 상태
**마케팅팀**: Properties → 캠페인, 채널, 예산, KPI 달성률
**HR팀**: Properties → 채용 단계, 지원자 수, 면접일, 합류 예정일
**디자인팀**: Properties → 프로젝트, 피그마 링크, 리뷰 상태, 마감일
**영업팀**: Properties → 거래처, 계약 단계, 금액, 미팅일
**스타트업 전체**: Properties → OKR, 분기 목표, 진행률, 담당 팀

## Formatting Rules

- Table view should be the DEFAULT view (overview first)
- Icon should match team context (🏠💼👥📊🚀)
- Sub-pages should have relevant icons
- Callout text should be professional yet friendly

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
- Primary: blue | Accent: gray | Secondary: blue
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 📢 공지사항 (callout, gray_background)
  - 📅 이번 주 일정 (callout, gray_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "우리 팀의 모든 정보가 여기에! 함께 성장하는 팀 홈 🏠" (blue_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with table view (기본), board view (상태별), calendar view (일정)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 팀 운영 가이드" with team rules and processes
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "team" (maps to themed Unsplash cover)
