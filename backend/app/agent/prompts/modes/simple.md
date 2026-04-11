## COMPLEXITY MODE: Simple (8-12 blocks, 1 DB)

This is a SIMPLE template. Keep it minimal and focused.
- 8-12 blocks total (no more)
- 1 database only
- 0-1 sub_pages
- 1-2 views per database (table + one more if it fits)
- NO column_list stat cards (overkill for simple templates)
- NO table_of_contents

### Simple Layout Flow:
callout(welcome) → paragraph("") →
heading_2(DB section title) → database_ref(0) →
paragraph("") → divider →
toggle("사용 가이드") → toggle("FAQ")

### Example: Simple Tracker
callout("💧 오늘도 물 한 잔! 건강한 습관을 기록하세요", orange_background)
→ paragraph("")
→ column_list(2col)[callout("📊 이번주 기록\n5회 달성") | callout("🎯 목표\n하루 8잔")]
→ paragraph("")
→ heading_2("💧 물 섭취 기록", orange)
→ database_ref(0)
→ paragraph("")
→ divider
→ toggle("📖 사용 가이드") → toggle("❓ FAQ")