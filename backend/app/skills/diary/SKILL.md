---
name: diary
parent: journal
description: 일기 및 하루 기록 트래커
keywords: 일기, 다이어리, 하루, 기록, 감정, diary, daily, journal
layout: simple_tracker
---
## DB Properties (required)
제목: title, 날짜: date, 기분: select(😄최고/😊좋음/😐보통/😟나쁨/😢최악), 날씨: select(☀️맑음/⛅흐림/🌧비/❄️눈), 내용: rich_text, 감사한것: rich_text

## Views
1. table (default) - 전체 일기 목록
2. calendar - 날짜별 일기 캘린더
3. gallery - 일기 카드 갤러리

## Block Pattern
heading("나의 일기장") → callout(오늘 하루를 기록하세요) → database(inline) → divider → toggle(일기 작성 팁) → quote(오늘도 수고했어요)

## Color Theme
pink + purple | cover: journal
