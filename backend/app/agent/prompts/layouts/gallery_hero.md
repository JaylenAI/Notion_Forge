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

### JSON Example (adapt, don't copy):
```json
{{
  "blocks": [
    {{"type": "callout", "icon": "📔", "color": "pink_background", "text": "나만의 기록을 남겨보세요",
      "children": [{{"type": "paragraph", "text": "소중한 순간을 기록하고, 나중에 돌아보는 즐거움을 느껴보세요."}}]
    }},
    {{"type": "paragraph", "text": ""}},
    {{"type": "quote", "text": "기록하지 않으면 기억나지 않는다.", "color": "pink"}},
    {{"type": "paragraph", "text": ""}},
    {{"type": "heading_1", "text": "📚 나의 컬렉션", "color": "pink"}},
    {{"type": "paragraph", "text": "갤러리 뷰에서 시각적으로 둘러보세요."}},
    {{"type": "database_ref", "db_index": 0}},
    {{"type": "paragraph", "text": ""}},
    {{"type": "divider"}},
    {{"type": "column_list", "columns": [
      [
        {{"type": "heading_3", "text": "📊 통계"}},
        {{"type": "callout", "icon": "📈", "color": "pink_background", "text": "총 기록\n42개"}},
        {{"type": "paragraph", "text": ""}},
        {{"type": "heading_3", "text": "🏷️ 카테고리"}},
        {{"type": "bulleted_list", "text": "소설 (15)"}},
        {{"type": "bulleted_list", "text": "자기계발 (12)"}},
        {{"type": "bulleted_list", "text": "기술 (8)"}},
        {{"type": "bulleted_list", "text": "에세이 (7)"}}
      ],
      [
        {{"type": "heading_3", "text": "⭐ 최근 추가"}},
        {{"type": "callout", "icon": "🆕", "color": "gray_background", "text": "이번 달 3개 추가!"}},
        {{"type": "paragraph", "text": ""}},
        {{"type": "heading_3", "text": "💡 활용 팁"}},
        {{"type": "bulleted_list", "text": "갤러리 뷰에서 커버 이미지를 활용하세요"}},
        {{"type": "bulleted_list", "text": "태그로 분류하면 검색이 편해요"}},
        {{"type": "bulleted_list", "text": "별점을 매기면 나중에 추천 목록을 만들 수 있어요"}}
      ]
    ]}},
    {{"type": "paragraph", "text": ""}},
    {{"type": "divider"}},
    {{"type": "toggle", "text": "📖 사용 가이드", "children": [
      {{"type": "numbered_list", "text": "1. 새 항목을 추가하세요 (제목 + 카테고리)"}},
      {{"type": "numbered_list", "text": "2. 커버 이미지를 설정하면 갤러리가 예뻐집니다"}},
      {{"type": "numbered_list", "text": "3. 평점과 메모를 남겨보세요"}}
    ]}}
  ]
}}
```

### When This Layout Works Best:
- Journals, diaries, mood trackers
- Recipe collections, book logs
- Wine/coffee tasting notes
- Photo albums, movie watchlists
- Any visual-first collection