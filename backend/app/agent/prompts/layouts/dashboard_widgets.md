## LAYOUT: Dashboard Widgets

A DATA-RICH dashboard with multiple linked_view widgets showing filtered slices of databases. Think CRM dashboard, analytics overview, or KPI tracker. Heavy use of columns and linked_views.

### Structure Pattern:
```
callout(welcome — professional: "대시보드에 오신 것을 환영합니다!")
paragraph("")
table_of_contents
paragraph("")
column_list(3col) [
  callout("📊 핵심 지표1\n수치", primary_bg) |
  callout("💰 핵심 지표2\n수치", accent_bg) |
  callout("📈 핵심 지표3\n수치", third_bg)
]
paragraph("")
divider
heading_1("📊 현황 요약")
column_list(2col) [
  LEFT:
    heading_3("🔥 긴급 항목")
    linked_view(0, list, filter: high_priority or this_week)
  |
  RIGHT:
    heading_3("✅ 최근 완료")
    linked_view(0, list, filter: status=완료)
]
paragraph("")
divider
heading_2("📋 전체 데이터")
database_ref(0) — with chart + table + board views
paragraph("")
divider
heading_2("💼 보조 데이터")
database_ref(1)
paragraph("")
divider
column_list(2col) [
  LEFT:
    heading_3("📈 트렌드")
    linked_view(0, chart, donut or column chart)
  |
  RIGHT:
    heading_3("📅 이번주 일정")
    linked_view(0 or 1, calendar)
]
paragraph("")
divider
toggle("📖 대시보드 가이드")
toggle("❓ FAQ")
```

### Key Principles:
- linked_view widgets are the CORE element — show filtered data slices
- Chart views for visual summaries (donut for status, column for trends)
- Use 2-column layouts to show related widgets side by side
- 3+ databases for complex dashboards (main data + supporting data)
- Blue for corporate, green for finance, purple for analytics
- table_of_contents REQUIRED for navigation
- Every widget should show DIFFERENT filtered data — not the same data repeated

### Database Views:
- Main DB: chart + board + table (3+ views)
- Supporting DBs: table + list (simpler)
- Use linked_view for filtered dashboard widgets

### When This Layout Works Best:
- CRM dashboards (customers + deals + activities)
- Sales pipelines
- KPI/OKR tracking
- Financial summaries
- Analytics overviews
- Team performance dashboards