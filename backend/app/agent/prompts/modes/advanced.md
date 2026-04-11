## COMPLEXITY MODE: Advanced (20-35 blocks, 2-4 DB)

This is an ADVANCED template. Go rich — multiple databases, linked views, sub-pages with real content.
- 20-35 blocks total
- 2-4 databases with relations between them
- 3-5 sub_pages with their OWN blocks
- 3-4 views per database
- column_list for stat cards AND for layout sections
- table_of_contents REQUIRED
- linked_view widgets for dashboard summaries
- tabs for organizing dense content

### Advanced Layout Flow:
callout(welcome) → table_of_contents → paragraph("") →
column_list(3col stat cards) → paragraph("") →
heading_1(Main DB section) → database_ref(0) → paragraph("") →
divider →
column_list(2col) [
  left: heading_2 + linked_view(filtered) + bulleted_list
  right: heading_2 + linked_view(filtered) + to_do list
] → paragraph("") →
heading_2(DB2 section) → database_ref(1) → paragraph("") →
divider →
heading_2(DB3 section) → database_ref(2) → paragraph("") →
divider →
toggle("사용 가이드") → toggle("FAQ")

### Example: Complex Dashboard (CRM, Life OS, School)
callout("🏢 CRM 대시보드에 오신 것을 환영합니다!", blue_background)
→ table_of_contents
→ paragraph("")
→ column_list(3col)[
    callout("📊 활성 고객\n128명", blue_bg) |
    callout("💰 이번달 매출\n₩45,000,000", green_bg) |
    callout("📈 전환율\n23%", purple_bg)
  ]
→ paragraph("")
→ heading_1("👥 고객 관리", blue)
→ database_ref(0)
→ paragraph("")
→ divider
→ heading_2("💼 거래 현황", green)
→ database_ref(1)
→ paragraph("")
→ column_list(2col)[
    heading_3("이번주 미팅") + linked_view(0, list, this_week filter) |
    heading_3("긴급 태스크") + linked_view(1, list, high_priority filter)
  ]
→ divider
→ heading_2("📊 활동 로그", purple)
→ database_ref(2)
→ paragraph("")
→ divider
→ toggle("📖 CRM 사용 가이드") → toggle("❓ FAQ")

### Pattern: Collection/Gallery (books, recipes, portfolio)
callout(welcome) → paragraph(empty) →
heading_1(collection) → paragraph(description) → database_ref(0) →
paragraph(empty) →
column_list(2col)[
  callout(stat)+bulleted_list(categories) |
  callout(stat)+bulleted_list(tags)
] → divider → toggle(guide)