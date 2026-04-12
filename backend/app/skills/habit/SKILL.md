---
name: habit
parent: track
description: 습관 추적 및 연속일수 관리 트래커
keywords: 습관, 루틴, 데일리, habit, routine, daily, streak, tracker
layout: simple_tracker
---
## DB Properties (required)
습관: title, 카테고리: select(건강/학습/생활), 날짜: date, 완료: checkbox, 연속일수: number, 메모: rich_text

## Views
1. calendar (default) - 월별 습관 완료 현황
2. table - 전체 습관 목록 및 연속일수 확인

## Block Pattern
heading("습관 트래커") → callout(이번 달 목표) → database(inline) → divider → toggle(습관 팁) → quote(꾸준함의 힘)

## Color Theme
purple + green | cover: minimal
