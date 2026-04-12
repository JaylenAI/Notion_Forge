---
name: gratitude
parent: journal
description: 감사 일기 및 긍정 기록
keywords: 감사, 긍정, 행복, 마음, gratitude, thankful, positive, mindful
layout: simple_tracker
---
## DB Properties (required)
감사제목: title, 날짜: date, 카테고리: select(사람/경험/자연/성장/일상), 기분: select(😊감사/🥰행복/😌평화/🤗따뜻), 내용: rich_text

## Views
1. table (default) - 전체 감사 기록 목록
2. calendar - 날짜별 감사 일기 캘린더
3. gallery - 감사 카드 갤러리

## Block Pattern
heading("감사 일기") → callout(오늘 감사한 일을 기록하세요) → database(inline) → divider → toggle(감사 습관 가이드) → quote(감사는 행복의 시작)

## Color Theme
yellow + orange | cover: nature
