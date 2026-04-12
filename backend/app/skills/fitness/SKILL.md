---
name: fitness
parent: track
description: 운동 기록 및 칼로리/부위별 분석 트래커
keywords: 운동, 헬스, 피트니스, 칼로리, fitness, workout, exercise, gym
layout: simple_tracker
---
## DB Properties (required)
운동명: title, 종류: select(유산소/근력/유연성), 시간(분): number, 칼로리: number, 부위: multi_select, 날짜: date, 완료: checkbox

## Views
1. calendar (default) - 날짜별 운동 기록 한눈에 보기
2. table - 전체 운동 목록 및 필터링
3. chart(donut) - 부위별/종류별 운동 비율

## Block Pattern
heading("운동 기록") → callout(오늘의 목표) → database(inline) → divider → toggle(주간 리포트) → quote(동기부여 문구)

## Color Theme
orange + green | cover: fitness
