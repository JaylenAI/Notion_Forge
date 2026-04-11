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

### When This Layout Works Best:
- Content calendars (blog, social media)
- Class schedules and timetables
- Event planning
- Editorial calendars
- Appointment scheduling