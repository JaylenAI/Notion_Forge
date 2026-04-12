---
name: cafe
parent: collect
description: 카페 탐방 기록 및 분위기별 정리
keywords: 카페, 커피, 맛집, cafe, coffee, review, place
layout: gallery_hero
---
## DB Properties (required)
카페명: title, 위치: rich_text, 메뉴: rich_text, 분위기: select(아늑한/모던/레트로/조용한), 평점: number, 방문일: date

## Views
1. gallery (default) - 카페 사진 갤러리
2. table - 전체 카페 목록 및 필터링
3. calendar - 방문 일정 보기

## Block Pattern
heading("카페 기록") → callout(이번 달 베스트) → database(inline) → divider → toggle(가고 싶은 카페) → quote(커피 한 잔의 여유)

## Color Theme
brown + orange | cover: food
