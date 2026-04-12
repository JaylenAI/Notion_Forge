---
name: goals
parent: plan
description: 목표/OKR 설정 및 진행률 추적 대시보드
keywords: 목표, OKR, 계획, 진행률, goals, objective, key result, progress
layout: dashboard_widgets
---
## DB Properties (required)
목표: title, 핵심결과: rich_text, 진행률: number, 기간: date, 카테고리: select(업무/개인/건강/학습), 상태: status

## Views
1. board (default) - 상태별 목표 보드
2. table - 전체 목표 및 진행률
3. chart - 카테고리별 달성률 차트

## Block Pattern
heading("목표 대시보드") → callout(올해의 핵심 목표) → database(inline) → divider → toggle(분기별 리뷰) → quote(목표 명언)

## Color Theme
blue + green | cover: business
