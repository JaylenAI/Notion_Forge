## LAYOUT: Sidebar + Main (2-Column)

This is the DEFAULT versatile layout. Use a 2-column structure where the LEFT column acts as a navigation sidebar and the RIGHT column is the main content area.

### Structure Pattern:
```
callout(welcome hero — full width)
paragraph("")
column_list(30/70 split) [
  LEFT SIDEBAR:
    callout("📌 빠른 링크", colored_bg) with navigation items
    paragraph("")
    callout("📊 통계 요약", colored_bg) with key metrics
    paragraph("")
    bulleted_list(categories or tags)
  |
  RIGHT MAIN:
    heading_2("📋 메인 섹션")
    paragraph(description)
    database_ref(0)
    paragraph("")
    heading_3("✏️ 빠른 메모") or to_do list
]
paragraph("")
divider
database_ref(1) — if second DB exists, put OUTSIDE columns at full width
paragraph("")
divider
toggle("📖 사용 가이드") with numbered_list children
toggle("❓ FAQ") with real Q&A pairs
```

### Key Principles:
- LEFT column = navigation + stats (compact, dense info)
- RIGHT column = main workspace (databases, content)
- database_ref MUST be at page level or inside the RIGHT column — NEVER in the left sidebar
- The sidebar callouts should use DIFFERENT icons and colors from the main content
- Sidebar width should feel ~30%, main ~70%

### When This Layout Works Best:
- General-purpose templates that don't fit a specific category
- Templates with mixed content types (DB + notes + links)
- Wiki-style knowledge bases
- Resource libraries