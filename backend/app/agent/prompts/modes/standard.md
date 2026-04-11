## COMPLEXITY MODE: Standard (12-20 blocks, 1-2 DB)

This is a STANDARD template. Balance richness with usability.
- 12-20 blocks total
- 1-2 databases
- 2-3 sub_pages
- 2-3 views per database
- column_list for stat cards (2-3 columns)
- table_of_contents if 15+ blocks

### Standard Layout Flow:
callout(welcome) → paragraph("") →
column_list(3col stat cards) → paragraph("") →
heading_2(DB1 section) → database_ref(0) → paragraph("") →
divider →
heading_2(DB2 section or action items) → database_ref(1) or to_do list →
paragraph("") → divider →
toggle("사용 가이드") → toggle("FAQ")

### Example: Project Board
callout("📋 프로젝트를 한눈에 관리하세요!", blue_background)
→ paragraph("")
→ column_list(3col)[callout("🔥 진행 중\n5건") | callout("📅 이번주 마감\n3건") | callout("✅ 완료율\n78%")]
→ paragraph("")
→ heading_2("📋 태스크 보드", blue)
→ database_ref(0)
→ paragraph("")
→ divider
→ heading_2("✏️ 오늘의 할일", blue)
→ to_do("기획서 초안 작성") → to_do("디자인 리뷰") → to_do("API 문서화")
→ paragraph("")
→ divider
→ toggle("📖 워크플로 가이드") → toggle("❓ FAQ")