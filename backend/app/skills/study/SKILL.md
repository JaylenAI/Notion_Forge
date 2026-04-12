---
name: study
parent: learn
description: 학습 시간 및 이해도 기록 트래커
keywords: 공부, 학습, 시험, 과목, study, learning, exam, subject
layout: simple_tracker
---
## DB Properties (required)
과목: title, 시간(분): number, 범위: rich_text, 이해도: select(상/중/하), 날짜: date, 메모: rich_text

## Views
1. table (default) - 전체 학습 기록 및 시간 합계
2. calendar - 날짜별 학습 현황
3. chart - 과목별 학습 시간 분석

## Block Pattern
heading("학습 기록") → callout(오늘의 학습 목표) → database(inline) → divider → toggle(시험 일정) → quote(배움의 즐거움)

## Color Theme
blue + purple | cover: study
