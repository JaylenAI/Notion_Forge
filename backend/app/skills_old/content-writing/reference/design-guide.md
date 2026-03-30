# Design Guide

## Color Theme Rules

### Apply background color to:
- heading_1, heading_2: `{color}_background`
- callout blocks: `{color}_background`
- navigation paragraph: `{color}_background`

### Do NOT apply to:
- paragraph (readability)
- bulleted_list (keep clean)
- to_do (checkbox conflict)

## Layout Patterns

### Dashboard (2-column)
- Left 30%: Navigation, section links
- Right 70%: Main content, action callouts
- Below columns: Inline database

### Note (2-column)
- Left 25%: Quick Action, Menu
- Right 75%: Guide, content
- Below: Inline database

### Simple (single)
- Callout → Divider → Heading → Database

## Block Order
1. Navigation bar
2. Divider
3. Welcome callout
4. Main content (columns)
5. Divider
6. DB heading
7. Inline database
8. FAQ toggles

## Icons
| Template | Icon | Section | Emoji |
|----------|------|---------|-------|
| Dashboard | 🏢 | Team | 👥 |
| Tracker | ✅ | Calendar | 📅 |
| Bookmark | 🔖 | Project | 📋 |
| Project | 📊 | Study | 📖 |
| Note | 📝 | Members | 👤 |
| Onboarding | 👋 | Settings | ⚙️ |
| CRM | 🤝 | | |
