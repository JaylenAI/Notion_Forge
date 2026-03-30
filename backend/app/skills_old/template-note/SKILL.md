---
name: template-note
description: Personal collection/journal note (Tea Note style) with Quick Action sidebar, record DB, and sub-pages.
triggers:
  - note
  - 노트
  - collection
  - 수집
  - journal
  - 일기
  - tasting
  - 시음
  - reading log
  - 독서
---

# Note Collection Template Skill

## When to Trigger
User mentions "note", "journal", "collection", "tasting record", "reading log".

## Page Structure
- **Icon**: 📝
- **Cover**: Theme-colored image

### Block Order
```
[2-column layout]
  Left 25%:
    👀 Callout: "Must read → Duplicate this template first!" [theme_bg]
    
    "Quick Action" [heading_2]
    ✏️ Callout: "New record" [theme_bg]
    📓 Callout: "Write journal" [theme_bg]
    
    Divider
    "Menu" [heading_2]
    → 📦 Inventory [link_to_page]
    → 📓 Journal [link_to_page]

  Right 75%:
    💡 Callout: "Usage guide" [theme_bg]
    Divider
    "Records" [heading_1, theme_bg]
    👇 Callout: "Manage records below" [theme_bg]

Divider
[Inline Database]
```

## Database Schema

| Property | Type | Options |
|----------|------|---------|
| 이름 | title | |
| 종류 | select | (AI infers from context) |
| 즐겨찾기 | checkbox | |
| 평점 | number | |
| 날짜 | date | |
| 메모 | rich_text | |

## Sub-Pages

| Page | Icon | Content |
|------|------|---------|
| Inventory | 📦 | Item management |
| Journal | 📓 | Daily entries |
