---
name: team_home
parent: hub
description: 팀 홈 대시보드 및 공지/일정 관리
keywords: 팀홈, 대시보드, 공지, 일정, team, home, dashboard, announcement
layout: dashboard_widgets
---
## DB Properties (required)
항목: title, 유형: select(공지/링크/목표/일정), 담당자: rich_text, 마감일: date, 중요도: select(높음/중간/낮음), 상태: status

## Views
1. table (default) - 전체 항목 목록 및 필터
2. board - 상태별 칸반 보드
3. calendar - 일정 및 마감일 캘린더

## Block Pattern
heading("팀 홈") → callout(팀 공지사항) → database(inline) → divider → toggle(팀 규칙 및 가이드) → toggle(유용한 링크 모음)

## Color Theme
blue + gray | cover: team
