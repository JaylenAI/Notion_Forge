---
name: sales
description: Creates sales pipeline templates for deal tracking, revenue forecasting, and opportunity management. Pipeline-driven with board and timeline views.
---

# Sales (영업 관리)

Creates templates for sales management including deal pipelines, revenue tracking, opportunity qualification, and performance dashboards.

## Quick Start

1. **Identify sales context**: What does the user want to manage? (deals, pipeline, quotas, forecasting)
2. **Design properties**: Always include select(stage) + number(amount) + date(close). Add context-specific fields.
3. **Set layout**: Two-column (left 25% revenue stats / right 75% pipeline DB)
4. **Add board view**: Essential for pipeline kanban visualization
5. **Generate samples**: 5+ deals at different pipeline stages with realistic data

## Template Structure

### Layout
Two-column (left 25% revenue stats callouts / right 75% pipeline database)

### Block Order
1. callout: Sales pipeline overview message (theme color, context icon)
2. column_list:
   - Column 1 (25%): Quarterly target callout + win rate callout
   - Column 2 (75%): Main pipeline content area
3. heading_1: Main title (theme color)
4. database_ref: Inline database here
5. divider
6. toggle: "Sales process guide" with stage definitions and tips

### Database Design

Required properties (always include):
- title: Deal/opportunity name
- select: Stage (리드/미팅/제안/협상/계약완료/실패)
- number: Deal amount (currency format)
- number: Win probability (percent format)
- date: Expected close date
- rich_text: Client/company name

Context-dependent properties (AI decides):
- rich_text: Contact person
- select: Source (인바운드/아웃바운드/소개/기존고객)
- select: Priority (긴급/높음/보통/낮음)
- rich_text: Next action
- email: Contact email
- select: Product/service line

### Views
- Required: board (PRIMARY - pipeline kanban by stage)
- Optional: timeline (deal progress and close dates)
- Optional: table (full deal list with amount totals)

### Sub-Pages
- "고객 미팅 노트" (Client Meeting Notes): Meeting records with agenda, attendees, and action items
- "제안서 템플릿" (Proposal Templates): Reusable proposal outlines and pricing structures
- "성과 리포트" (Performance Report): Monthly/quarterly sales performance summary

### Sample Data
Generate 5+ deals at different pipeline stages with realistic Korean business data.
Each item needs: relevant icon, stage, deal amount, probability, close date, and client name.

## Content Adaptation Examples

**B2B Pipeline**: Properties → company, stage, deal value, decision maker, competitor, proposal date, contract term
**Quota Tracking**: Properties → rep name, target(number), achieved(number), attainment %(formula), remaining days
**Lead Qualification**: Properties → lead source, BANT score(number), qualification status, first contact date, industry(select)
**Account Management**: Properties → account name, ARR(number), renewal date, health score(select), upsell opportunity(checkbox)

## Formatting Rules

- Callout icon should match context (💼 sales, 🎯 target, 📈 pipeline, 🤝 deal)
- Board view is the PRIMARY view (pipeline visualization is essential)
- Keep properties under 9 (sales needs detail but stay manageable)
- Number properties should use Korean Won format for amounts
- Summary callouts should show pipeline total, quarterly target, and win rate

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic close dates within ±1 month
- Amount values: realistic Korean B2B deal sizes (500만원, 1,200만원, 3,500만원, 8,000만원, 1.5억원)
- Stage values: spread across all pipeline stages (리드, 미팅, 제안, 협상, 계약완료, 실패)
- Probability values: match stage (리드 10%, 미팅 25%, 제안 50%, 협상 75%, 계약완료 100%)
- Source values: mix of 인바운드, 아웃바운드, 소개
- Client names: realistic Korean company names (넥스트테크, 한울금융, 미래유통, 그린제조, 블루서비스)
- Contact: realistic Korean business contacts (김이사, 박팀장, 이부장, 최대리, 정과장)

## Pro Design Guide

### Color Palette
- Primary: blue | Accent: orange | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (25%): stat callouts
  - 🎯 분기 목표 (callout, orange_background)
  - 💰 파이프라인 총액 (callout, orange_background)
  - 📈 승률 (callout, orange_background)
- RIGHT (75%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "모든 기회를 파이프라인으로 관리하세요! 데이터 기반 영업의 시작 💼" (blue_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with board view (기본, 파이프라인 칸반), timeline view (마감일), table view (상세 목록)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "business" (maps to themed Unsplash cover)
