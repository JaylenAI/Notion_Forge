## LAYOUT: Portfolio / Resume

A SHOWCASE layout designed to present work, skills, and experience beautifully. The page itself IS the content — it reads like a personal website or resume.

### Structure Pattern:
```
callout(hero — name + title + brief intro, primary_bg)
  rich_text: [{"text": "이름", "bold": true, "color": "primary"}, {"text": " — 직함/한줄 소개"}]
paragraph("")
column_list(2col) [
  LEFT:
    heading_3("📍 정보")
    paragraph("이메일: example@email.com")
    paragraph("위치: 서울")
    paragraph("")
    heading_3("🛠️ 기술 스택")
    bulleted_list("Python / FastAPI")
    bulleted_list("React / TypeScript")
    bulleted_list("PostgreSQL / Redis")
  |
  RIGHT:
    heading_3("💼 경력 요약")
    callout("N년차 직무 전문가", accent_bg)
    paragraph("")
    quote("개인 미션 스테이트먼트 또는 좌우명")
]
paragraph("")
divider
heading_1("🎨 포트폴리오")
paragraph("주요 프로젝트와 작업물을 소개합니다.")
database_ref(0) — gallery view with project covers
paragraph("")
divider
heading_2("💼 경력 사항")
database_ref(1) — timeline or table view for career history
paragraph("")
divider
heading_2("🏆 수상 및 자격")
bulleted_list("수상1 — 날짜")
bulleted_list("자격증1 — 날짜")
bulleted_list("수상2 — 날짜")
paragraph("")
divider
heading_2("📫 연락하기")
callout("프로젝트 협업이나 문의는 아래로 연락 주세요!", accent_bg)
paragraph("이메일: example@email.com")
bookmark("https://github.com/username")
bookmark("https://linkedin.com/in/username")
```

### Key Principles:
- The PAGE IS the portfolio — it should read top to bottom like a personal site
- Gallery view for projects with visual covers (large cover_size)
- Timeline view for career history (start/end dates)
- Use rich_text formatting for emphasis (bold names, colored highlights)
- Professional but personal tone
- Purple/blue for tech, pink/creative for design, green for business
- Bookmarks for external links (GitHub, LinkedIn, personal site)
- NO toggle guides — this isn't a tool, it's a showcase

### Database Views:
- Projects DB: gallery (default, large covers) + table
- Career DB: timeline (default) + table

### JSON Example (adapt, don't copy):
```json
{{
  "blocks": [
    {{"type": "callout", "icon": "👤", "color": "purple_background", "text": "포트폴리오",
      "rich_text": [{{"text": "홍길동", "bold": true, "color": "purple"}}, {{"text": " — 풀스택 개발자"}}]
    }},
    {{"type": "paragraph", "text": ""}},
    {{"type": "column_list", "columns": [
      [
        {{"type": "heading_3", "text": "📍 정보"}},
        {{"type": "paragraph", "text": "이메일: hello@example.com"}},
        {{"type": "paragraph", "text": "위치: 서울"}},
        {{"type": "paragraph", "text": ""}},
        {{"type": "heading_3", "text": "🛠️ 기술 스택"}},
        {{"type": "bulleted_list", "text": "Python / FastAPI"}},
        {{"type": "bulleted_list", "text": "React / TypeScript"}},
        {{"type": "bulleted_list", "text": "PostgreSQL / Redis"}}
      ],
      [
        {{"type": "heading_3", "text": "💼 경력 요약"}},
        {{"type": "callout", "icon": "🏢", "color": "gray_background", "text": "5년차 백엔드 엔지니어"}},
        {{"type": "paragraph", "text": ""}},
        {{"type": "quote", "text": "좋은 코드는 읽기 쉬운 코드입니다.", "color": "purple"}}
      ]
    ]}},
    {{"type": "paragraph", "text": ""}},
    {{"type": "divider"}},
    {{"type": "heading_1", "text": "🎨 프로젝트", "color": "purple"}},
    {{"type": "paragraph", "text": "주요 프로젝트와 작업물을 소개합니다."}},
    {{"type": "database_ref", "db_index": 0}},
    {{"type": "paragraph", "text": ""}},
    {{"type": "divider"}},
    {{"type": "heading_2", "text": "🏆 수상 및 자격", "color": "purple"}},
    {{"type": "bulleted_list", "text": "AWS Solutions Architect — 2025"}},
    {{"type": "bulleted_list", "text": "정보처리기사 — 2024"}},
    {{"type": "paragraph", "text": ""}},
    {{"type": "divider"}},
    {{"type": "heading_2", "text": "📫 연락하기", "color": "purple"}},
    {{"type": "callout", "icon": "📬", "color": "purple_background", "text": "프로젝트 협업이나 문의는 아래로 연락 주세요!"}},
    {{"type": "bookmark", "url": "https://github.com/username"}},
    {{"type": "bookmark", "url": "https://linkedin.com/in/username"}}
  ]
}}
```

### When This Layout Works Best:
- Developer portfolios
- Designer showcases
- Freelancer profiles
- Resume/CV pages
- Personal introduction pages
- Artist galleries