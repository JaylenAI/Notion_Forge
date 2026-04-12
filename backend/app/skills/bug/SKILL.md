---
name: bug
parent: manage
description: 버그 리포트 추적 및 심각도별 관리 보드
keywords: 버그, 이슈, 결함, 트래커, bug, issue, defect, tracker
layout: kanban_board
---
## DB Properties (required)
버그: title, 심각도: select(Critical/High/Medium/Low), 상태: status, 재현경로: rich_text, 담당자: rich_text, 발견일: date

## Views
1. board (default) - 상태별 버그 칸반
2. table - 전체 버그 목록 및 필터링

## Block Pattern
heading("버그 트래커") → callout(긴급 이슈) → database(inline) → divider → toggle(해결 가이드) → toggle(릴리즈 노트)

## Color Theme
red + gray | cover: tech
