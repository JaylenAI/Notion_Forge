## LAYOUT: Gallery Hero

The GALLERY view is the star of this template. Design everything around visual browsing — the database should be in gallery view by default, with large cover images.

### Structure Pattern:
```
callout(welcome — warm, personal tone, with quote-like text)
paragraph("")
quote("기록은 기억이 됩니다." or similar inspirational line, colored)
paragraph("")
heading_1("📚 나의 컬렉션" — single main heading)
paragraph(collection description — what's being collected and why)
database_ref(0) — gallery view as DEFAULT, then table as secondary
paragraph("")
divider
column_list(2col) [
  LEFT:
    heading_3("📊 통계")
    callout("총 N개 기록" stat card)
    paragraph("")
    heading_3("🏷️ 카테고리")
    bulleted_list(categories)
  |
  RIGHT:
    heading_3("⭐ 즐겨찾기")
    callout("최근 추가된 항목" highlight)
    paragraph("")
    heading_3("💡 팁")
    bulleted_list(usage tips)
]
paragraph("")
divider
toggle("📖 사용 가이드")
```

### Key Principles:
- Gallery view MUST be the FIRST/default view with cover images
- Use page_cover or page_content for gallery card covers
- cover_size: "medium" or "large" — make it visual
- The quote block adds personality — personal/journal templates need warmth
- Stats go BELOW the gallery, not above — let the visual content shine first
- Use pink/purple/warm tones for personal, orange/green for food/recipes

### Database Views Order:
1. gallery (default, with covers)
2. table (fallback for data entry)
3. calendar (if date property exists)

### When This Layout Works Best:
- Journals, diaries, mood trackers
- Recipe collections, book logs
- Wine/coffee tasting notes
- Photo albums, movie watchlists
- Any visual-first collection