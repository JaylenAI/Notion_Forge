---
name: bug
description: Creates bug tracking templates for issue reports, severity management, reproduction steps, and resolution workflows. Status-driven with board and table views.
---

# Bug (버그 트래커)

Creates templates for bug tracking including issue reporting, severity classification, reproduction tracking, and resolution management.

## Quick Start

1. **Identify bug tracking context**: What does the user want to track? (bugs, issues, defects, crash reports)
2. **Design properties**: Always include status + select(severity) + rich_text(reproduction). Add context-specific fields.
3. **Set layout**: Two-column (left 25% critical stats / right 75% bug board)
4. **Add board view**: Essential for bug status kanban visualization
5. **Generate samples**: 5+ bugs at different severity levels with realistic data

## Template Structure

### Layout
Two-column (left 25% critical stats / right 75% bug board)

### Block Order
1. callout: Critical issues alert message (theme color, context icon)
2. column_list:
   - Column 1 (25%): Open bugs callout + critical count callout + resolved this week callout
   - Column 2 (75%): Main bug board content area
3. divider
4. heading_1: Main title (theme color)
5. database_ref: Inline database here
6. toggle: "버그 리포트 작성 가이드" with report template
7. toggle: "릴리즈 노트 템플릿" with release note structure

### Database Design

Required properties (always include):
- title: Bug title
- select: Severity (Critical/High/Medium/Low)
- status: Stage (신규/확인됨/수정중/테스트중/해결/보류)
- rich_text: Reproduction steps
- rich_text: Assignee
- date: Reported date

Context-dependent properties (AI decides):
- select: Platform (Web/iOS/Android/Server)
- select: Component (프론트엔드/백엔드/DB/인프라)
- rich_text: Expected vs actual behavior
- rich_text: Reporter
- url: Screenshot/recording link
- select: Version (v1.0/v1.1/v2.0)

### Views
- Required: board (PRIMARY - bug status kanban)
- Optional: table (all bugs with filtering and sorting by severity)
- Optional: board (grouped by severity for triage)

### Sub-Pages
- "버그 리포트 템플릿" (Bug Report Template): Standardized format for reporting bugs
- "릴리즈 노트" (Release Notes): Fixed bugs per release version with changelog
- "알려진 이슈" (Known Issues): Documented known bugs with workarounds

### Sample Data
Generate 5+ bugs at different severity levels with realistic Korean dev data.
Each item needs: relevant icon, severity, status, reproduction steps, assignee, and date.

## Content Adaptation Examples

**Web App Bugs**: Properties → bug title, severity, page/URL, browser(select), status, screenshot(url), console error(rich_text)
**Mobile App Bugs**: Properties → bug title, severity, device(select), OS version, status, crash log(rich_text), build number
**API Bugs**: Properties → endpoint, method(GET/POST/PUT/DELETE), status code, expected response, actual response, severity
**UX Issues**: Properties → issue, page, severity, user impact(select), proposed fix(rich_text), designer(rich_text)

## Formatting Rules

- Callout icon should match context (🐛 bug, 🚨 critical, ⚠️ warning, 🔧 fix)
- Board view is the PRIMARY view (bug workflow tracking is essential)
- Keep properties under 10 (bug reports need clarity, not complexity)
- Severity options should use color coding (Critical=red, High=orange, Medium=yellow, Low=gray)
- Quick stats callout should show key counts (전체 버그, Critical 수, 이번 주 해결)

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±1 week
- Severity values: spread across Critical, High, Medium, Low (1 Critical, 1 High, 2 Medium, 1 Low)
- Status values: spread across 신규, 확인됨, 수정중, 테스트중, 해결
- Platform values: mix of Web, iOS, Android
- Bug titles: realistic Korean bug descriptions (로그인 시 앱 크래시 발생, 결제 완료 후 주문 상태 미반영, 프로필 이미지 업로드 실패, 검색 결과 정렬 오류, 다크모드 전환 시 텍스트 안보임)
- Reproduction: realistic step-by-step (1. 로그인 화면 진입 2. 소셜 로그인 클릭 3. 카카오 선택 4. 앱 크래시)
- Assignee: realistic Korean developer names (김민수, 이서연, 박준호, 최지원, 정우진)

## Pro Design Guide

### Color Palette
- Primary: red | Accent: orange | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (25%): stat callouts
  - 🐛 전체 버그 (callout, orange_background)
  - 🚨 Critical (callout, orange_background)
  - ✅ 이번 주 해결 (callout, orange_background)
- RIGHT (75%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "버그를 체계적으로 추적하고 빠르게 해결하세요! 🐛" (red_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with board view (기본, 상태별 칸반), table view (전체 버그), board view (심각도별)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "tech" (maps to themed Unsplash cover)
