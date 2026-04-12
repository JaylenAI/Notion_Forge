---
name: wedding
parent: plan
description: 결혼 준비 항목별 예산 및 진행 상태 관리
keywords: 결혼, 웨딩, 예식, 신혼, wedding, marriage, planning, budget
layout: category_hub
---
## DB Properties (required)
항목: title, 카테고리: select(예식/신혼여행/예물/촬영/청첩장), 예산: number, 실제비용: number, 상태: status, D-Day: date

## Views
1. board (default) - 상태별 진행 보드
2. table - 전체 항목 및 예산 비교
3. calendar - D-Day 기준 일정

## Block Pattern
heading("웨딩 플래너") → callout(D-Day 카운트다운) → database(inline) → divider → toggle(예산 총정리) → toggle(체크리스트)

## Color Theme
pink + purple | cover: minimal
