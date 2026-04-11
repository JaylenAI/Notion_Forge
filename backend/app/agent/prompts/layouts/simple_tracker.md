## LAYOUT: Simple Tracker

MINIMAL and FOCUSED. One database, clean layout, no clutter. The user wants to track something specific — don't over-engineer it. Less is more.

### Structure Pattern:
```
callout(welcome — casual, encouraging: "오늘도 한 걸음! 꾸준히 기록해보세요 💪")
paragraph("")
column_list(2col) [
  callout("📊 이번주\nN회 달성", primary_bg) |
  callout("🎯 목표\n하루 N회", accent_bg)
]
paragraph("")
heading_2("📋 기록 현황")
database_ref(0) — table view as default, simple and clean
paragraph("")
divider
quote("꾸준함이 최고의 재능이다." — motivational)
paragraph("")
toggle("📖 사용 가이드") with 3 simple steps
toggle("❓ FAQ") with 2 common questions
```

### Key Principles:
- MAXIMUM 12 blocks — resist the urge to add more
- ONE database only — no second DB, no sub_pages
- 4-6 properties per database (keep it light)
- Table view as default (simple, data-entry friendly)
- Calendar as secondary view IF date property exists
- Chart view for visual motivation IF it makes sense
- Warm, encouraging tone — this is personal tracking
- Orange/green for health, blue for productivity

### Database Views Order (pick 1-2):
1. table (default — simple data entry)
2. calendar (if tracking daily)
3. chart (optional — for visual motivation)

### What NOT to Do:
- NO column_list with 3+ columns (too complex for a tracker)
- NO table_of_contents (too short to need it)
- NO sub_pages (keep everything on one page)
- NO linked_views (unnecessary complexity)
- NO more than 1 database

### When This Layout Works Best:
- Water intake tracking
- Exercise/workout logs
- Sleep tracking
- Habit streaks
- Simple expense logging
- Reading progress
- Any single-metric daily tracker