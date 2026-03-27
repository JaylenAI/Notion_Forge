---
name: template-dashboard
description: Project/schedule management dashboard with 2-column layout (sidebar + main), navigation bar, inline DB, sub-pages, and action callouts.
triggers:
  - dashboard
  - 대시보드
  - home
  - main
  - to-do list
  - schedule
---

# Dashboard Template Skill

## When to Trigger
User mentions "dashboard", "to-do list", "schedule management", "home page", or similar.

## Page Structure

### Main Page
- **Icon**: 🏢
- **Cover**: Theme-colored image from Unsplash

### Block Order
1. Navigation bar (paragraph with theme background)
2. Divider
3. 2-column layout (left 30% / right 70%)
4. Divider
5. Database heading (heading_2, theme background)
6. Inline database (To-Do List)

### Left Sidebar (30%)
```
💡 Callout: "Add calendar view from the DB menu :)" [theme_bg]
Divider
---
"Team" [heading_2, theme_bg]
  → 👥 Members [link_to_page]
  → 📅 Calendar [link_to_page]

"Project" [heading_2, theme_bg]
  → 📋 Project [link_to_page]

"Study" [heading_2, theme_bg]
  → 📖 Study [link_to_page]
```

### Right Main (70%)
```
"To-Do List" [heading_1, theme_bg]
Divider
✅ Callout: "To Do List 추가하기" [theme_bg]
🗓️ Callout: "회의록 추가하기" [theme_bg]
📋 Callout: "스터디 일정 추가하기" [theme_bg]
📝 Callout: "기타 일정 추가하기" [theme_bg]
Divider
👇 Callout: "Manage your schedule in the database below" [theme_bg]
```

## Database Schema: To-Do List

| Property | Type | Options |
|----------|------|---------|
| 이름 | title | |
| 날짜 | date | |
| 설명 | rich_text | |
| 진행사항 | status | 시작 전, 진행 중, 완료 |
| 태그 | multi_select | ETC(yellow), Study(blue), Meeting(purple), To-Do List(orange), Project(green) |

## Sample Data (5 items)

| 이름 | 날짜 | 태그 | Icon |
|------|------|------|------|
| 고객사 출장 | +0d | ETC | ⭐ |
| 노션팀 1주차 스터디 | +1d | Study | 📌 |
| 노션팀 주간 미팅 | +3d | Meeting | 📁 |
| 마케팅 홍보 자료 제작하기 | +4d | To-Do List | ⬜ |
| Q2 목표 설정 | +7d | Project | 🎯 |

## Sub-Pages

| Page | Icon | Content |
|------|------|---------|
| Members | 👥 | Team member list, roles |
| Calendar | 📅 | Schedule management guide |
| Project | 📋 | Project tracking |
| Study | 📖 | Study/learning management |

Each sub-page contains:
- heading_1 (icon + title, theme_bg)
- Guide callout
- Divider
