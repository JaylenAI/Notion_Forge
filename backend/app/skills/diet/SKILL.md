---
name: diet
parent: track
description: 식단 및 칼로리/영양소 관리 트래커
keywords: 식단, 다이어트, 칼로리, 영양, diet, meal, calorie, nutrition
layout: simple_tracker
---
## DB Properties (required)
식사: title, 구분: select(아침/점심/저녁/간식), 칼로리: number, 단백질: number, 날짜: date, 메모: rich_text

## Views
1. table (default) - 전체 식단 기록 및 영양소 확인
2. calendar - 날짜별 식단 보기

## Block Pattern
heading("식단 기록") → callout(일일 목표 칼로리) → database(inline) → divider → toggle(영양 가이드) → quote(건강한 식습관)

## Color Theme
green + orange | cover: food
