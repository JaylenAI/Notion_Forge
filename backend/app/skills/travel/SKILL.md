---
name: travel
parent: plan
description: 여행 일정 및 예산/예약 관리 플래너
keywords: 여행, 일정, 예산, 예약, travel, trip, itinerary, booking
layout: calendar_main
---
## DB Properties (required)
항목: title, 카테고리: select(교통/숙소/관광/식사/쇼핑), 날짜: date, 비용: number, 예약상태: status, 메모: rich_text

## Views
1. calendar (default) - 여행 일정 캘린더
2. table - 전체 항목 및 비용 합계
3. board - 예약상태별 보드

## Block Pattern
heading("여행 플래너") → callout(여행 정보) → database(inline) → divider → toggle(짐 체크리스트) → toggle(비용 정산)

## Color Theme
orange + blue | cover: travel
