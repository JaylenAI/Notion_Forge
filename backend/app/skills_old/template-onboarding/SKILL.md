---
name: template-onboarding
description: New employee onboarding guide with weekly checklists, handover DB, and FAQ toggles.
triggers:
  - onboarding
  - 온보딩
  - 인수인계
  - new employee
  - 신입
  - guide
---

# Onboarding Template Skill

## When to Trigger
User mentions "onboarding", "new hire", "handover", "orientation guide".

## Page Structure
- **Icon**: 👋
- **Cover**: Theme-colored image

### Block Order
```
👋 Callout: "Welcome! This is your onboarding guide. Follow step by step!" [theme_bg]
Divider

"📋 Week 1: First Steps" [heading_2, theme_bg]
  ☐ Account setup (email, Slack, Jira)
  ☐ Team meeting
  ☐ Dev environment setup
  ☐ Read internal wiki

"📋 Week 2: Explore" [heading_2, theme_bg]
  ☐ Codebase exploration
  ☐ First PR
  ☐ Join code review
  ☐ Understand team culture

"📋 Week 3: Practice" [heading_2, theme_bg]
  ☐ Independent task
  ☐ Documentation
  ☐ Suggest improvements

"📋 Week 4: Settle In" [heading_2, theme_bg]
  ☐ Project assignment
  ☐ Onboarding retrospective
  ☐ 1:1 meeting

Divider
"📊 Handover Status" [heading_1, theme_bg]
[Inline Database]

Divider
"💡 FAQ" [heading_2, theme_bg]
▶ Wi-Fi password? → "Ask admin team."
▶ PTO request? → "Apply via HR system."
▶ Equipment request? → "Post in IT Slack channel."
▶ Lunch spots? → "Check the team Notion food page! 🍚"
```

## Database Schema

| Property | Type | Options |
|----------|------|---------|
| 항목 | title | |
| 담당자 | rich_text | |
| 상태 | status | 시작 전, 진행 중, 완료 |
| 기한 | date | |
| 비고 | rich_text | |

## Sample Data (4 items)

| 항목 | Icon |
|------|------|
| 계정 발급 (이메일, Slack) | 🔑 |
| 개발환경 세팅 | 💻 |
| 코드리뷰 프로세스 안내 | 📖 |
| 배포 프로세스 안내 | 🚀 |
