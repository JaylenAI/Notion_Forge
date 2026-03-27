---
name: template-crm
description: Customer/sales CRM with pipeline status tracking, contact info, and deal management.
triggers:
  - crm
  - 고객
  - customer
  - sales
  - 영업
  - 거래처
  - pipeline
---

# CRM Template Skill

## When to Trigger
User mentions "CRM", "customer management", "sales pipeline", "deal tracking".

## Page Structure
- **Icon**: 🤝
- **Cover**: Theme-colored image

### Block Order
```
🤝 Callout: "Manage customers systematically! Filter by status for pipeline view." [theme_bg]
Divider
"📋 Customer List" [heading_1, theme_bg]
[Inline Database]
Divider
💡 Toggle: "Pipeline Guide"
  → "Lead → Meeting → Proposal → Contract"
```

## Database Schema

| Property | Type | Options |
|----------|------|---------|
| 고객명 | title | |
| 회사 | rich_text | |
| 상태 | select | 리드(gray), 미팅(blue), 제안(orange), 계약(green) |
| 연락처 | email | |
| 최근 연락 | date | |
| 메모 | rich_text | |
| 예상 매출 | number | |

## Sample Data (3 items)

| 고객명 | Icon |
|--------|------|
| 김철수 | 👤 |
| 이영희 | 👤 |
| 박지수 | 👤 |
