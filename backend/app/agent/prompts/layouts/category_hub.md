## LAYOUT: Category Hub

A STRUCTURED hub page with clear sections organized by category. Think company wiki, team home, or onboarding portal. Heavy use of toggles and sub-pages for organized navigation.

### Structure Pattern:
```
callout(welcome — professional, clear, with team/org name)
paragraph("")
table_of_contents
paragraph("")
column_list(3col) [
  callout("👥 팀원\nN명", stat) |
  callout("📄 문서\nN개", stat) |
  callout("✅ 완료율\nN%", stat)
]
paragraph("")
divider
heading_1("📁 카테고리별 안내")
paragraph("")
heading_3("📋 시작하기", is_toggleable=true) [
  numbered_list("1단계: ...")
  numbered_list("2단계: ...")
  numbered_list("3단계: ...")
]
paragraph("")
heading_3("📚 자료실", is_toggleable=true) [
  bulleted_list("회사 소개서")
  bulleted_list("브랜드 가이드라인")
  bulleted_list("기술 문서")
]
paragraph("")
heading_3("❓ 자주 묻는 질문", is_toggleable=true) [
  toggle("Q: 질문1") with answer
  toggle("Q: 질문2") with answer
]
paragraph("")
divider
heading_2("📊 진행 현황")
database_ref(0)
paragraph("")
divider
toggle("📖 관리자 가이드")
```

### Key Principles:
- Toggle headings (heading_3 with is_toggleable=true) are the CORE navigation element
- Organize content into 3-5 clear categories
- Use sub_pages for deep content (each sub-page = one category)
- table_of_contents is REQUIRED for navigation
- Professional tone — no overly casual emoji
- Blue/gray color scheme for corporate, green for education

### Sub-pages Pattern:
Each hub should have 2-4 sub_pages like:
- "📋 시작 가이드" — onboarding steps
- "📚 자료실" — documents and resources
- "❓ FAQ" — detailed Q&A
- "⚙️ 설정" — configuration and preferences

### When This Layout Works Best:
- Company/team wikis and hubs
- Onboarding portals
- Course or class home pages
- Documentation centers
- Department home pages