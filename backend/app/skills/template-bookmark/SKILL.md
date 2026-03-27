---
name: template-bookmark
description: Bookmark/site organizer with category sidebar and gallery DB. Supports favorites and routine filtering.
triggers:
  - bookmark
  - 북마크
  - favorites
  - 즐겨찾기
  - link collection
  - site organizer
---

# Bookmark Template Skill

## When to Trigger
User mentions "bookmark", "favorites", "link organizer", "site collection".

## Page Structure
- **Icon**: 🔖
- **Cover**: Theme-colored image

### Block Order
```
[2-column layout]
  Left 30%:
    "📂 Category" [heading_2, theme_bg]
    • 커리어
    • 쇼핑
    • 교육/툴&디자인
    • 뉴스/매거진
    • Entertain
    
  Right 70%:
    ⭐ Callout: "Check favorites to quickly find your go-to sites." [theme_bg]
    📌 Callout: "Set days in routine property for auto-filtering." [theme_bg]
    Divider
    "🔖 Bookmarks" [heading_1, theme_bg]
    👇 Callout: "Manage bookmarks below" [theme_bg]

Divider
[Inline Database]
```

## Database Schema

| Property | Type | Options |
|----------|------|---------|
| 이름 | title | |
| URL | url | |
| 카테고리 | select | 커리어(blue), 쇼핑(red), 교육/툴(green), 뉴스(orange), 엔터(purple), 게임(pink) |
| 즐겨찾기 | checkbox | |
| 메모 | rich_text | |

## Sample Data (5 items)

| 이름 | Icon |
|------|------|
| Google | 🔍 |
| GitHub | 🐙 |
| Notion | 📓 |
| Figma | 🎨 |
| YouTube | 📺 |
