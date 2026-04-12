## LAYOUT: Kanban Board

The BOARD VIEW is the hero. This layout is optimized for workflow management — tasks flow through status columns. Everything supports the board view experience.

### Structure Pattern:
```
callout(welcome — action-oriented: "프로젝트를 체계적으로 관리하세요!")
paragraph("")
column_list(3col) [
  callout("🔥 진행 중\nN건", orange_bg) |
  callout("📅 이번주 마감\nN건", yellow_bg) |
  callout("✅ 완료율\nN%", green_bg)
]
paragraph("")
heading_2("📋 태스크 보드")
database_ref(0) — board view as DEFAULT
paragraph("")
divider
heading_2("✏️ 오늘의 할일")
to_do("우선순위 높은 작업 1")
to_do("우선순위 높은 작업 2")
to_do("우선순위 높은 작업 3")
paragraph("")
divider
heading_2("📊 프로젝트 타임라인")
database_ref(0 or 1) — timeline view or linked_view with date filter
paragraph("")
divider
numbered_list("1. 새 태스크를 추가합니다")
numbered_list("2. 상태를 '진행 중'으로 변경합니다")
numbered_list("3. 완료되면 '완료'로 이동합니다")
paragraph("")
toggle("📖 워크플로 가이드") with detailed steps
toggle("❓ FAQ")
```

### Key Principles:
- Board view MUST be the FIRST/default view (group_by status)
- Status property is REQUIRED: "시작 전", "진행 중", "완료"
- to_do blocks for daily action items — keeps users engaged
- Timeline view as secondary for date-based planning
- Orange/blue for urgency, green for completion
- Stat cards show WORKFLOW metrics (not generic stats)

### Database Views Order:
1. board (default, grouped by 상태)
2. timeline (for date planning)
3. table (data entry fallback)
4. calendar (if date property exists)

### JSON Example (adapt, don't copy):
```json
{{
  "blocks": [
    {{"type": "callout", "icon": "📋", "color": "blue_background", "text": "프로젝트를 체계적으로 관리하세요!",
      "children": [{{"type": "paragraph", "text": "칸반 보드에서 태스크 상태를 한눈에 확인하고 관리할 수 있습니다."}}]
    }},
    {{"type": "paragraph", "text": ""}},
    {{"type": "column_list", "columns": [
      [{{"type": "callout", "icon": "🔥", "color": "orange_background", "text": "진행 중\n5건"}}],
      [{{"type": "callout", "icon": "📅", "color": "yellow_background", "text": "이번주 마감\n3건"}}],
      [{{"type": "callout", "icon": "✅", "color": "green_background", "text": "완료율\n78%"}}]
    ]}},
    {{"type": "paragraph", "text": ""}},
    {{"type": "heading_2", "text": "📋 태스크 보드", "color": "blue"}},
    {{"type": "database_ref", "db_index": 0}},
    {{"type": "paragraph", "text": ""}},
    {{"type": "divider"}},
    {{"type": "heading_2", "text": "✏️ 오늘의 할일", "color": "blue"}},
    {{"type": "to_do", "text": "우선순위 높은 태스크 확인"}},
    {{"type": "to_do", "text": "팀 미팅 준비"}},
    {{"type": "to_do", "text": "코드 리뷰 완료"}},
    {{"type": "paragraph", "text": ""}},
    {{"type": "divider"}},
    {{"type": "toggle", "text": "📖 워크플로 가이드", "children": [
      {{"type": "numbered_list", "text": "1. 새 태스크를 추가합니다"}},
      {{"type": "numbered_list", "text": "2. 상태를 '진행 중'으로 변경합니다"}},
      {{"type": "numbered_list", "text": "3. 완료되면 '완료'로 이동합니다"}},
      {{"type": "callout", "icon": "💡", "color": "yellow_background", "text": "팁: 타임라인 뷰에서 마감일을 시각적으로 확인하세요"}}
    ]}}
  ]
}}
```

### When This Layout Works Best:
- Project management
- Sprint planning
- Bug tracking
- Content pipelines
- Any status-driven workflow