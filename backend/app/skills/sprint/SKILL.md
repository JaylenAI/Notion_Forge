---
name: sprint
parent: manage
description: 스프린트 기반 애자일 개발 관리 보드
keywords: 스프린트, 애자일, 스크럼, 스토리, sprint, agile, scrum, story
layout: kanban_board
---
## DB Properties (required)
스토리: title, 상태: status, 포인트: number, 스프린트: select(Sprint1/Sprint2/Sprint3), 에픽: select, 담당자: rich_text

## Views
1. board (default) - 상태별 칸반 보드
2. table - 전체 스토리 목록 및 포인트 합계

## Block Pattern
heading("스프린트 보드") → callout(스프린트 목표) → database(inline) → divider → toggle(번다운 차트) → toggle(회고)

## Color Theme
blue + orange | cover: tech
