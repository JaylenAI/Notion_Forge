---
name: project
parent: manage
description: 프로젝트 태스크 관리 칸반 보드
keywords: 프로젝트, 태스크, 업무, 관리, project, task, kanban, management
layout: kanban_board
---
## DB Properties (required)
태스크: title, 상태: status, 담당자: rich_text, 우선순위: select(긴급/높음/보통/낮음), 카테고리: select(기획/개발/디자인/QA), 마감일: date

## Views
1. board (default) - 상태별 칸반 보드
2. timeline - 타임라인 뷰
3. table - 전체 태스크 목록
4. calendar - 마감일 기준 캘린더

## Block Pattern
heading("프로젝트 보드") → callout(프로젝트 목표) → database(inline) → divider → toggle(마일스톤) → toggle(회의록)

## Color Theme
blue + gray | cover: business
