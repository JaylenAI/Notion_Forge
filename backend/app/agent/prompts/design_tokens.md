## BLOCK DIVERSITY RULES (CRITICAL!)
You MUST use diverse blocks. Do NOT repeat the same callout→column→toggle pattern every time.

### MANDATORY BLOCK MIX:
- Every template MUST include at least 3 of these: quote, to_do, numbered_list, bulleted_list, bookmark
- Tracking templates: MUST include to_do (daily checklist) + quote (motivation)
- Management templates: MUST include numbered_list (workflow steps) + to_do (action items)
- Finance templates: MUST include bulleted_list (categories) + quote (financial goal)
- Collection templates: MUST include bulleted_list (categories) + bookmark (resources)
- Learning templates: MUST include numbered_list (study steps) + to_do (tasks) + bookmark (resources)
- CRM/Hub templates: MUST include sub_pages (2-3 linked pages) + multiple database_ref

### TOGGLE CONTENT RULES:
- Toggle "사용 가이드" MUST contain numbered_list with 3-5 setup steps, NOT just a paragraph
- Toggle "FAQ" MUST contain 2-3 real question/answer pairs
- Use toggle children_text for simple FAQs, use children array with numbered_list for guides

### TABLE_OF_CONTENTS RULE:
- Templates with 15+ blocks MUST include table_of_contents at the top (after welcome callout)

### SUB_PAGES RULE:
- Complex templates (hub, CRM, multi-DB) MUST include 2-3 sub_pages
- Each sub_page MUST have blocks array with real content (callout + heading + paragraphs/lists)
- NEVER create empty sub_pages — they must have useful content inside
- Example sub_page blocks: callout(intro) + heading_2(section) + bulleted_list(items) + toggle(tips)

### COVER_CATEGORY RULE:
- ALWAYS set cover_category matching the template topic:
  business, finance, fitness, study, travel, food, creative, nature, tech, minimal

### MULTI-DB RULE:
- Simple requests: 1 database, 0-1 sub_pages
- Medium requests: 1-2 databases, 2-3 sub_pages
- Complex requests (hub, CRM, startup, school): 3-4 databases + 5-8 sub_pages
- Each database should serve a DIFFERENT purpose (tasks vs schedule vs resources vs contacts)

### SUB_PAGES DEPTH RULE:
- Sub-pages MUST have their OWN blocks (callout + heading + content + toggle)
- Complex sub-pages can have their OWN databases (add separate database specs)
- Sub-pages should be organized by CATEGORY (e.g., 자료실, 설정, 아카이브)

## DESIGN TOKEN SYSTEM (per-category consistency)
Each template category has a fixed design token set. ALWAYS follow these:

### Business/Project: icons: 🎯📊📋✅ | blue + gray | cover: business
  - Callout: blue_background | Headings: blue
  - DB icons: 📊📋🗂️ | Status: blue(active), green(done), gray(default)

### Fitness/Health: icons: 💪🏋️🏃🧘 | orange + green | cover: fitness
  - Callout: orange_background | Headings: orange

### Finance: icons: 💰📈🏦💵 | green + gray | cover: finance
  - Callout: green_background | Headings: green
  - Select: green(income), red(expense), blue(savings)

### Creative/Content: icons: 🎨📱✨🎬 | purple + pink | cover: creative
  - Callout: purple_background | Headings: purple

### Learning/Study: icons: 📚🎓📖✏️ | blue + purple | cover: study
  - Callout: blue_background | Headings: blue

### Personal/Journal: icons: 📔✨🌸💭 | pink + gray | cover: minimal
  - Callout: pink_background | Headings: pink

### CRM/Sales: icons: 🤝📞💼🎯 | blue + orange | cover: business
### Travel/Plan: icons: ✈️🗺️📍🌍 | orange + blue | cover: travel
### Food/Recipe: icons: 🍽️🧑‍🍳🥗🍰 | orange + green | cover: food

## ANTI-PATTERNS: NEVER DO THESE
- NEVER use more than 3 colors (looks chaotic)
- NEVER skip whitespace paragraphs between sections (looks cramped)
- NEVER put more than 8 properties per database (overwhelming)
- NEVER create pages deeper than 2 levels (buried content)
- NEVER put everything on one flat list (use columns, toggles)
- NEVER mix random emoji styles (pick consistent icons)
- NEVER skip the welcome callout (every pro template has one)
- NEVER forget the usage guide toggle (users need instructions)
- NEVER leave sample data empty (minimum 5 realistic items per DB)
- NEVER use divider between every block (only between MAJOR sections)
- NEVER put database_ref inside column_list (Notion API cannot render DB inside columns)