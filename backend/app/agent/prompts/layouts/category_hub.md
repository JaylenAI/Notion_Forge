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

### JSON Example (adapt, don't copy):
```json
{{
  "blocks": [
    {{"type": "callout", "icon": "🏢", "color": "blue_background", "text": "팀 허브에 오신 것을 환영합니다!",
      "children": [
        {{"type": "paragraph", "text": "필요한 모든 자료와 가이드를 한곳에서 찾아보세요."}},
        {{"type": "bulleted_list", "text": "📋 시작 가이드"}},
        {{"type": "bulleted_list", "text": "📚 자료실"}},
        {{"type": "bulleted_list", "text": "❓ FAQ"}}
      ]
    }},
    {{"type": "paragraph", "text": ""}},
    {{"type": "table_of_contents", "color": "gray"}},
    {{"type": "paragraph", "text": ""}},
    {{"type": "column_list", "columns": [
      [{{"type": "callout", "icon": "👥", "color": "blue_background", "text": "팀원\n12명"}}],
      [{{"type": "callout", "icon": "📄", "color": "green_background", "text": "문서\n34개"}}],
      [{{"type": "callout", "icon": "✅", "color": "purple_background", "text": "완료율\n89%"}}]
    ]}},
    {{"type": "paragraph", "text": ""}},
    {{"type": "divider"}},
    {{"type": "heading_1", "text": "📁 카테고리별 안내", "color": "blue"}},
    {{"type": "paragraph", "text": ""}},
    {{"type": "heading_3", "text": "📋 시작하기", "is_toggleable": true, "children": [
      {{"type": "numbered_list", "text": "1. 팀 소개 문서를 읽어주세요"}},
      {{"type": "numbered_list", "text": "2. 필수 도구를 설치하세요"}},
      {{"type": "numbered_list", "text": "3. 슬랙 채널에 인사해주세요"}},
      {{"type": "callout", "icon": "💡", "color": "yellow_background", "text": "첫 주에 모든 것을 완료하지 않아도 괜찮아요!"}}
    ]}},
    {{"type": "paragraph", "text": ""}},
    {{"type": "heading_3", "text": "📚 자료실", "is_toggleable": true, "children": [
      {{"type": "bulleted_list", "text": "회사 소개서"}},
      {{"type": "bulleted_list", "text": "브랜드 가이드라인"}},
      {{"type": "bulleted_list", "text": "기술 문서"}}
    ]}},
    {{"type": "paragraph", "text": ""}},
    {{"type": "heading_3", "text": "❓ 자주 묻는 질문", "is_toggleable": true, "children": [
      {{"type": "toggle", "text": "Q: 비밀번호를 잊었어요", "children": [{{"type": "paragraph", "text": "A: IT 지원팀에 문의하세요."}}]}},
      {{"type": "toggle", "text": "Q: 재택근무 신청은 어떻게?", "children": [{{"type": "paragraph", "text": "A: HR 포탈에서 신청서를 작성하세요."}}]}}
    ]}},
    {{"type": "paragraph", "text": ""}},
    {{"type": "divider"}},
    {{"type": "heading_2", "text": "📊 진행 현황", "color": "blue"}},
    {{"type": "database_ref", "db_index": 0}}
  ]
}}
```

### When This Layout Works Best:
- Company/team wikis and hubs
- Onboarding portals
- Course or class home pages
- Documentation centers
- Department home pages