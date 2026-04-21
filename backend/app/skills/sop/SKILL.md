---
name: sop
description: Creates standard operating procedure templates for process documentation, review cycles, and department-based workflow management. Process-driven with table and board views.
---

# SOP (표준 운영 절차)

Creates templates for standard operating procedure management including process documentation, review scheduling, department workflows, and compliance tracking.

## Quick Start

1. **Identify SOP context**: What does the user want to document? (daily ops, compliance, department procedures, emergency protocols)
2. **Design properties**: Always include select(department) + select(frequency) + status(review status). Add context-specific fields.
3. **Set layout**: Two-column (left 30% overview stats / right 70% SOP DB)
4. **Add table view**: Essential for department-based filtering and search
5. **Generate samples**: 5+ SOPs across departments with realistic process data

## Template Structure

### Layout
Two-column (left 30% SOP overview callouts / right 70% procedure database)

### Block Order
1. callout: SOP management overview message (theme color, context icon)
2. column_list:
   - Column 1 (30%): Total procedures callout + review due callout
   - Column 2 (70%): Main SOP content area
3. heading_1: Main title (theme color)
4. database_ref: Inline database here
5. divider
6. toggle: "SOP writing guidelines" with formatting standards and templates

### Database Design

Required properties (always include):
- title: Procedure name
- select: Department (개발/디자인/마케팅/영업/인사/총무)
- select: Frequency (매일/매주/매월/분기/필요시)
- rich_text: Responsible person/owner
- date: Last reviewed date
- status: Status (초안/검토중/승인됨/개정필요)

Context-dependent properties (AI decides):
- number: Version number
- rich_text: Summary/purpose
- select: Risk level (높음/중간/낮음)
- date: Next review date
- url: Related document link
- multi_select: Related departments

### Views
- Required: table (PRIMARY - full SOP list with department filtering)
- Optional: board (department-based grouping)

### Sub-Pages
- "절차 작성 가이드라인" (Writing Guidelines): Standards for creating and formatting SOPs
- "검토 주기 안내" (Review Cycle Guide): Review frequency rules and escalation process
- "변경 이력" (Change Log): SOP revision history and approval records

### Sample Data
Generate 5+ SOPs across departments with realistic Korean corporate process data.
Each item needs: relevant icon, department, frequency, owner, review date, and status.

## Content Adaptation Examples

**Operations SOP**: Properties → procedure, department, frequency(매일/매주), owner, checklist steps(rich_text), last incident date
**Compliance**: Properties → regulation name, requirement(rich_text), audit frequency, responsible, evidence link(url), risk level
**Emergency Protocol**: Properties → scenario, severity(select), response steps(rich_text), contact list, drill date, last updated
**IT Procedures**: Properties → procedure, system affected(multi_select), access level(select), automation status(select), runbook link(url)

## Formatting Rules

- Callout icon should match context (📋 procedure, 🔄 process, ⚙️ operations, 🛡️ compliance)
- Table view is the PRIMARY view (department filtering and search are key)
- Keep properties under 8 (procedures need clarity, not complexity)
- Status should reflect a clear review lifecycle
- Summary callouts should show total SOPs, approved count, and review-due count

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic review dates within ±3 months
- Procedure names: realistic Korean corporate SOPs (서버 배포 절차, 신규 채용 프로세스, 고객 클레임 처리, 월말 정산 절차, 보안 사고 대응)
- Department values: spread across 개발, 디자인, 마케팅, 영업, 인사, 총무
- Frequency values: mix of 매일, 매주, 매월, 분기, 필요시
- Status values: mostly 승인됨, 1-2 검토중 or 개정필요
- Owner: realistic Korean corporate roles (개발팀 김시니어, 인사팀 박매니저, 영업팀 이팀장, 총무팀 최주임, 마케팅팀 정대리)
- Version: realistic version numbers (1.0, 1.2, 2.0, 3.1)

## Pro Design Guide

### Color Palette
- Primary: gray | Accent: blue | Secondary: default
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 📋 전체 SOP 수 (callout, blue_background)
  - ✅ 승인 완료 (callout, blue_background)
  - 🔄 검토 필요 (callout, blue_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "표준화된 절차로 업무 품질을 높이세요! 체계적인 프로세스 관리 📋" (gray_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with table view (기본, 전체 SOP 목록), board view (부서별)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "document" (maps to themed Unsplash cover)
