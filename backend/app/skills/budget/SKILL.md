---
name: budget
parent: finance
description: 수입/지출/저축 가계부 및 카테고리별 분석
keywords: 가계부, 예산, 지출, 수입, budget, expense, income, finance
layout: dashboard_widgets
---
## DB Properties (required)
내역: title, 금액: number, 구분: select(수입/지출/저축), 카테고리: select(식비/교통/문화/생활/급여), 날짜: date, 메모: rich_text

## Views
1. table (default) - 전체 내역 목록 및 합계
2. calendar - 날짜별 수입/지출 보기
3. chart(donut) - 카테고리별 지출 비율

## Block Pattern
heading("가계부") → callout(이번 달 예산) → database(inline) → divider → toggle(월별 정산) → toggle(절약 팁)

## Color Theme
green + gray | cover: finance
