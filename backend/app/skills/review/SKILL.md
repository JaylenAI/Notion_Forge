---
name: review
parent: journal
description: 주간/월간 회고 및 목표 달성 리뷰
keywords: 회고, 리뷰, 주간, 월간, 분기, 연간, review, retrospective, reflection
layout: simple_tracker
---
## DB Properties (required)
기간: title, 유형: select(주간/월간/분기/연간), 잘한점: rich_text, 개선점: rich_text, 다음목표: rich_text, 달성률: number, 날짜: date

## Views
1. table (default) - 전체 회고 기록 목록
2. gallery - 회고 카드 갤러리

## Block Pattern
heading("회고 노트") → callout(정기적으로 돌아보는 습관) → database(inline) → divider → toggle(회고 작성 프레임워크) → toggle(KPT 가이드)

## Color Theme
green + blue | cover: reflection
