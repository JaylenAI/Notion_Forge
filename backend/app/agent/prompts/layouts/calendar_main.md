## LAYOUT: Calendar Main

The CALENDAR VIEW is the centerpiece. Everything revolves around dates and scheduling. The page is designed for time-based planning.

### Structure Pattern:
```
callout(welcome — time-focused: "일정을 한눈에 관리하세요!")
paragraph("")
column_list(2col) [
  LEFT:
    callout("📅 이번주\nN건 예정", primary_bg)
    paragraph("")
    callout("⏰ 오늘\nN건", accent_bg)
  |
  RIGHT:
    heading_3("⚡ 빠른 추가")
    to_do("새 일정 추가하기")
    to_do("마감일 확인하기")
    paragraph("")
    heading_3("🏷️ 카테고리")
    bulleted_list(category items)
]
paragraph("")
heading_2("📅 캘린더")
database_ref(0) — calendar view as DEFAULT
paragraph("")
divider
heading_2("📋 전체 일정 목록")
linked_view(0, table, sorted by date) or database_ref with table view
paragraph("")
divider
quote("계획 없는 목표는 그저 소원일 뿐이다.")
paragraph("")
toggle("📖 사용 가이드")
toggle("❓ FAQ")
```

### Key Principles:
- Calendar view MUST be the FIRST/default view
- Date property is REQUIRED and must be prominently used
- Show upcoming events with linked_view filtered to "this_week" or "next_7_days"
- Use column layout for quick-add + category sidebar
- Include a motivational quote related to planning/time
- Blue/purple for professional, orange for creative scheduling

### Database Views Order:
1. calendar (default)
2. table (sorted by date)
3. board (if status property exists)
4. timeline (if start+end dates exist)

### JSON Example (adapt, don't copy):
```json
{{
  "blocks": [
    {{"type": "callout", "icon": "📅", "color": "blue_background", "text": "일정을 한눈에 관리하세요!",
      "children": [{{"type": "paragraph", "text": "캘린더에서 전체 일정을 확인하고, 새 일정을 추가해보세요."}}]
    }},
    {{"type": "paragraph", "text": ""}},
    {{"type": "column_list", "columns": [
      [
        {{"type": "callout", "icon": "📅", "color": "blue_background", "text": "이번주\n5건 예정"}},
        {{"type": "paragraph", "text": ""}},
        {{"type": "callout", "icon": "⏰", "color": "orange_background", "text": "오늘\n2건"}}
      ],
      [
        {{"type": "heading_3", "text": "⚡ 빠른 추가"}},
        {{"type": "to_do", "text": "새 일정 추가하기"}},
        {{"type": "to_do", "text": "마감일 확인하기"}},
        {{"type": "paragraph", "text": ""}},
        {{"type": "heading_3", "text": "🏷️ 카테고리"}},
        {{"type": "bulleted_list", "text": "업무"}},
        {{"type": "bulleted_list", "text": "개인"}},
        {{"type": "bulleted_list", "text": "미팅"}}
      ]
    ]}},
    {{"type": "paragraph", "text": ""}},
    {{"type": "heading_2", "text": "📅 캘린더", "color": "blue"}},
    {{"type": "database_ref", "db_index": 0}},
    {{"type": "paragraph", "text": ""}},
    {{"type": "divider"}},
    {{"type": "quote", "text": "계획 없는 목표는 그저 소원일 뿐이다.", "color": "blue"}},
    {{"type": "paragraph", "text": ""}},
    {{"type": "toggle", "text": "📖 사용 가이드", "children": [
      {{"type": "numbered_list", "text": "1. 캘린더에서 날짜를 클릭하여 새 일정 추가"}},
      {{"type": "numbered_list", "text": "2. 카테고리별로 필터링하여 확인"}},
      {{"type": "numbered_list", "text": "3. 테이블 뷰에서 전체 목록 관리"}}
    ]}}
  ]
}}
```

### When This Layout Works Best:
- Content calendars (blog, social media)
- Class schedules and timetables
- Event planning
- Editorial calendars
- Appointment scheduling