---
name: recipe
parent: collect
description: 요리 레시피 수집 및 카테고리별 관리
keywords: 요리, 레시피, 식재료, recipe, cooking, food, cuisine
layout: gallery_hero
---
## DB Properties (required)
요리명: title, 카테고리: select(한식/양식/중식/일식/디저트), 난이도: select(쉬움/보통/어려움), 조리시간: number, 재료: rich_text, 날짜: date

## Views
1. gallery (default) - 요리 사진 갤러리
2. table - 전체 레시피 목록 및 필터링

## Block Pattern
heading("레시피 모음") → callout(이번 주 식단) → database(inline) → divider → toggle(장보기 목록) → quote(요리는 사랑)

## Color Theme
orange + green | cover: food
