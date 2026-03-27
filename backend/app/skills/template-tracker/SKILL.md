---
name: template-tracker
description: Daily habit/goal tracker with checkbox DB, categories, usage guide toggle.
triggers:
  - tracker
  - 트래커
  - habit
  - 습관
  - routine
  - goal
---

# Tracker Template Skill

## When to Trigger
User mentions "tracker", "habit", "routine", "daily check", "goal tracking".

## Page Structure
- **Icon**: ✅
- **Cover**: Theme-colored image

### Block Order
```
🎯 Callout: "Build habits by checking every day! Small habits create big changes." [theme_bg]
Divider
"📋 Today's Tasks" [heading_1, theme_bg]
[Inline Database]
Divider
💡 Toggle: "How to use"
  → "Open this page every morning and check completed items. Filter by category."
```

## Database Schema

| Property | Type | Options |
|----------|------|---------|
| 항목 | title | |
| 카테고리 | select | 건강(green), 학습(blue), 생활(orange), 자기계발(purple) |
| 완료 | checkbox | |
| 날짜 | date | |
| 메모 | rich_text | |

## Sample Data (7 items)

| 항목 | 카테고리 | Icon |
|------|---------|------|
| 운동 30분 | 건강 | 💪 |
| 독서 1시간 | 학습 | 📚 |
| 명상 10분 | 건강 | 🧘 |
| 영어 회화 연습 | 자기계발 | 🇺🇸 |
| 물 2L 마시기 | 생활 | 💧 |
| 일기 쓰기 | 자기계발 | ✏️ |
| 비타민 챙기기 | 건강 | 💊 |
