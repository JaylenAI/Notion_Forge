---
name: health
parent: track
description: 수면/물/체중/혈압 등 건강 지표 기록 트래커
keywords: 건강, 수면, 체중, 혈압, health, sleep, weight, blood pressure
layout: simple_tracker
---
## DB Properties (required)
기록: title, 유형: select(수면/물/체중/혈압), 수치: number, 단위: rich_text, 날짜: date, 메모: rich_text

## Views
1. table (default) - 전체 건강 기록 목록
2. calendar - 날짜별 기록 확인
3. chart - 수치 변화 추이 그래프

## Block Pattern
heading("건강 기록") → callout(오늘의 컨디션) → database(inline) → divider → toggle(건강 목표) → quote(건강이 최고의 재산)

## Color Theme
blue + green | cover: nature
