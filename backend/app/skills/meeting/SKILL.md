---
name: meeting
parent: manage
description: 회의 일정 관리 및 회의록/액션아이템 기록
keywords: 회의, 미팅, 회의록, 일정, meeting, minutes, schedule, action
layout: calendar_main
---
## DB Properties (required)
회의명: title, 참석자: rich_text, 날짜: date, 유형: select(정기/임시/1:1/전체), 액션아이템: rich_text, 메모: rich_text

## Views
1. calendar (default) - 회의 일정 캘린더
2. table - 전체 회의 목록
3. list - 최근 회의 리스트

## Block Pattern
heading("회의 관리") → callout(이번 주 일정) → database(inline) → divider → toggle(회의 템플릿) → toggle(액션아이템 현황)

## Color Theme
blue + green | cover: business
