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

### JSON Example (adapt, don't copy):
```json
{{
  "blocks": [
    {{"type": "callout", "icon": "🏠", "color": "blue_background", "text": "나만의 워크스페이스",
      "children": [{{"type": "paragraph", "text": "모든 것을 한곳에서 관리하세요."}}]
    }},
    {{"type": "paragraph", "text": ""}},
    {{"type": "column_list", "width_ratios": [30, 70], "columns": [
      [
        {{"type": "callout", "icon": "📌", "color": "blue_background", "text": "빠른 링크",
          "children": [
            {{"type": "bulleted_list", "text": "📊 대시보드"}},
            {{"type": "bulleted_list", "text": "📋 태스크"}},
            {{"type": "bulleted_list", "text": "📅 캘린더"}}
          ]
        }},
        {{"type": "paragraph", "text": ""}},
        {{"type": "callout", "icon": "📈", "color": "green_background", "text": "이번주 요약\n완료 8건 / 진행 3건"}}
      ],
      [
        {{"type": "heading_2", "text": "📋 메인 보드", "color": "blue"}},
        {{"type": "database_ref", "db_index": 0}},
        {{"type": "paragraph", "text": ""}},
        {{"type": "heading_3", "text": "✏️ 빠른 메모"}},
        {{"type": "to_do", "text": "오늘 할 일 정리"}},
        {{"type": "to_do", "text": "주간 리뷰 작성"}}
      ]
    ]}},
    {{"type": "paragraph", "text": ""}},
    {{"type": "divider"}},
    {{"type": "toggle", "text": "📖 사용 가이드", "children": [
      {{"type": "numbered_list", "text": "1. 왼쪽 사이드바에서 빠르게 이동하세요"}},
      {{"type": "numbered_list", "text": "2. 메인 보드에서 태스크를 관리하세요"}},
      {{"type": "numbered_list", "text": "3. 빠른 메모로 잊지 않도록 기록하세요"}}
    ]}}
  ]
}}
```

### When This Layout Works Best:
- General-purpose templates that don't fit a specific category
- Templates with mixed content types (DB + notes + links)
- Wiki-style knowledge bases
- Resource libraries