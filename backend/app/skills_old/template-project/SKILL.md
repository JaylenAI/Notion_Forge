---
name: template-project
description: Project/task management board with status tracking, priority, and assignees. Kanban-ready.
triggers:
  - project
  - 프로젝트
  - kanban
  - 칸반
  - sprint
  - task board
  - 태스크
---

# Project Board Template Skill

## When to Trigger
User mentions "project", "task board", "kanban", "sprint planning".

## Page Structure
- **Icon**: 📊
- **Cover**: Theme-colored image

### Block Order
```
📊 Callout: "Track project progress at a glance. Add Board view for kanban!" [theme_bg]
Divider
"🗂️ Task Board" [heading_1, theme_bg]
[Inline Database]
Divider
💡 Toggle: "How to use"
  → "Change status to track progress. Add Board view for kanban layout."
```

## Database Schema

| Property | Type | Options |
|----------|------|---------|
| 태스크 | title | |
| 상태 | status | 시작 전, 진행 중, 완료 |
| 담당자 | rich_text | |
| 우선순위 | select | 높음(red), 중간(yellow), 낮음(green) |
| 기한 | date | |
| 카테고리 | select | 기획(blue), 디자인(purple), 개발(green), QA(orange) |

## Sample Data (5 items)

| 태스크 | Icon |
|--------|------|
| 기획서 작성 | 📝 |
| 디자인 시안 | 🎨 |
| 백엔드 개발 | ⚙️ |
| 프론트엔드 개발 | 🖥️ |
| QA 테스트 | 🧪 |
