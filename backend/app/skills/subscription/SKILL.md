---
name: subscription
description: Creates subscription management templates for tracking recurring payments, billing cycles, and service status. Table-driven with calendar views.
---

# Subscription (구독 관리)

Creates templates for subscription and recurring payment management including service tracking, billing schedules, cost analysis, and cancellation planning.

## Quick Start

1. **Identify subscription context**: What does the user want to manage? (streaming, SaaS, memberships, utilities)
2. **Design properties**: Always include number(amount) + date(billing) + select(status). Add context-specific fields.
3. **Set layout**: Two-column (left 30% cost summary / right 70% subscription DB)
4. **Add table view**: Essential for cost overview and filtering
5. **Generate samples**: 5+ subscriptions with realistic Korean service data

## Template Structure

### Layout
Two-column (left 30% cost summary callouts / right 70% subscription database)

### Block Order
1. callout: Subscription overview message (theme color, context icon)
2. column_list:
   - Column 1 (30%): Monthly total callout + upcoming payments callout
   - Column 2 (70%): Main subscription content area
3. heading_1: Main title (theme color)
4. database_ref: Inline database here
5. divider
6. toggle: "Subscription review guide" with cost optimization tips

### Database Design

Required properties (always include):
- title: Service name
- number: Monthly fee (currency format)
- date: Next billing date
- select: Status (활성/해지예정/일시정지/해지)
- select: Category (엔터테인먼트/생산성/교육/건강/뉴스/클라우드)

Context-dependent properties (AI decides):
- select: Billing cycle (월간/연간/분기)
- select: Payment method (카드/계좌이체/간편결제)
- url: Service URL
- rich_text: Memo/notes
- checkbox: Auto-renewal

### Views
- Required: table (PRIMARY - full subscription list with monthly totals)
- Optional: calendar (billing date calendar view)

### Sub-Pages
- "해지 검토 리스트" (Cancellation Review): Services to evaluate for cancellation with cost-benefit notes
- "무료 대안 목록" (Free Alternatives): Free or cheaper alternatives for current paid services

### Sample Data
Generate 5+ subscriptions representing realistic Korean digital service usage.
Each item needs: relevant icon, filled amount, billing date, status, and category.

## Content Adaptation Examples

**Streaming**: Properties → service, monthly fee, sharing(checkbox), profile count(number), platform(Netflix/Disney+/Wavve/Tving)
**SaaS Tools**: Properties → service, plan tier(select), seats(number), annual cost, renewal date, admin contact
**Memberships**: Properties → gym/club name, monthly fee, contract end date, benefits(rich_text), auto-renewal
**Utilities**: Properties → utility type(전기/가스/수도/인터넷), monthly average, provider, contract period, bill date

## Formatting Rules

- Callout icon should match context (🔄 subscription, 💳 payment, 📺 streaming, 🛠️ SaaS)
- Table view is the PRIMARY view (cost comparison needs columns)
- Keep properties under 8 (focused on cost tracking)
- Number properties should use Korean Won format (₩17,000/월)
- Summary callouts should show monthly total and upcoming payment count

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic billing dates within current month
- Amount values: realistic Korean subscription prices (넷플릭스 17,000원, 스포티파이 10,900원, 유튜브 프리미엄 14,900원, 노션 15,000원, 쿠팡와우 4,990원)
- Status values: mostly 활성, 1-2 해지예정 or 일시정지
- Category values: spread across entertainment, productivity, education
- Billing cycle: mix of 월간 and 연간

## Pro Design Guide

### Color Palette
- Primary: yellow | Accent: orange | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 💳 월 구독료 합계 (callout, orange_background)
  - 📅 이번 주 결제 예정 (callout, orange_background)
  - 🔄 활성 구독 수 (callout, orange_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "구독 서비스를 한눈에 관리하세요! 불필요한 지출을 줄여보세요 💳" (yellow_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with table view (기본, 전체 구독 목록), calendar view (결제일)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "tech" (maps to themed Unsplash cover)
