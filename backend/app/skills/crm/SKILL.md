---
name: crm
description: Creates customer and relationship management templates for clients, sales pipelines, meeting notes, and lead tracking. Status-driven with board and timeline views.
---

# CRM (고객 관리)

Creates templates for customer and relationship management including client tracking, sales pipelines, meeting notes, and lead management.

## Quick Start

1. **Identify CRM context**: What does the user want to manage? (clients, sales pipeline, leads, meetings)
2. **Design properties**: Always include status + date(follow-up) + rich_text(contact). Add context-specific fields.
3. **Set layout**: Two-column (left 25% quick stats / right 75% pipeline DB)
4. **Add board view**: Essential for sales pipeline kanban visualization
5. **Generate samples**: 5 clients at different pipeline stages with realistic data

## Template Structure

### Layout
Two-column (left 25% quick stats / right 75% pipeline database)

### Block Order
1. callout: CRM overview message (theme color, context icon)
2. column_list:
   - Column 1 (25%): Quick stats summary callout + recent activity callout
   - Column 2 (75%): Main pipeline content area
3. divider
4. heading_1: Main title (theme color)
5. database_ref: Inline database here
6. toggle: "Sales process guide" with stage descriptions and tips

### Database Design

Required properties (always include):
- title: Client/company name
- status: Pipeline stage (리드/미팅/제안/협상/계약완료/실패)
- date: Next follow-up date
- rich_text: Contact person name

Context-dependent properties (AI decides):
- number: Deal value (currency format)
- email: Contact email
- select: Industry (IT/금융/유통/제조/서비스)
- select: Priority (Hot/Warm/Cold)
- url: Company website
- rich_text: Notes/history

### Views
- Required: board (PRIMARY - sales pipeline kanban by status)
- Optional: timeline (deal progress over time)
- Optional: table (all details in spreadsheet format)

### Sub-Pages
- "미팅 노트" (Meeting Notes): Records of client meetings with agenda and action items
- "제안서 템플릿" (Proposal Templates): Reusable proposal structures and outlines
- "고객 히스토리" (Client History): Detailed interaction history per client

### Sample Data
Generate 5 clients at different pipeline stages with realistic Korean business data.
Each item needs: relevant icon, status, deal value, contact info, and follow-up date.

## Content Adaptation Examples

**Sales Pipeline**: Properties → company, status(리드→계약완료), deal value, probability(number), close date, owner
**Client Management**: Properties → company, industry, contract value, renewal date, satisfaction score(number), account manager
**Lead Tracking**: Properties → source(inbound/outbound/referral), status, qualification score(number), first contact date, assigned to
**Meeting Notes**: Properties → client, date, attendees(multi_select), agenda(rich_text), action items(rich_text), next meeting date

## Formatting Rules

- Callout icon should match context (🤝 client, 💼 sales, 📞 lead, 📋 meeting)
- Board view is the PRIMARY view (pipeline visualization is key for CRM)
- Keep properties under 9 (CRM needs more fields but should stay manageable)
- Status options should reflect a clear sales funnel progression
- Quick stats callout should show key metrics (total deals, pipeline value, win rate)

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic follow-up dates within ±2 weeks
- Status values: spread across all pipeline stages (리드, 미팅, 제안, 협상, 계약완료, 실패)
- Deal values: realistic Korean business amounts (500만원, 1,200만원, 3,000만원, 8,500만원, 2억원)
- Industry values: use different industries for variety (IT, 금융, 유통, 제조, 서비스)
- Priority values: mix of Hot, Warm, Cold
- Contact: realistic Korean business contacts (김팀장, 이사업부장, 박대리, etc.)
- Company names: realistic Korean company names (테크솔루션즈, 한빛금융, 그린유통, etc.)

## Pro Design Guide

### Color Palette
- Primary: blue | Accent: orange | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 👥 총 고객 (callout, orange_background)
  - 💼 진행 중 딜 (callout, orange_background)
  - 💰 이번 달 매출 (callout, orange_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "고객과의 관계를 체계적으로 관리하세요! 모든 딜을 한눈에 🤝" (blue_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with board view (기본, 파이프라인 칸반), timeline view (딜 진행), table view (상세)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "business" (maps to themed Unsplash cover)
