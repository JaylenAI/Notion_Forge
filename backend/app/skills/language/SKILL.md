---
name: language
parent: learn
description: 외국어 단어장 및 숙달도별 복습 관리
keywords: 외국어, 단어, 영어, 일본어, language, vocabulary, word, review
layout: gallery_hero
---
## DB Properties (required)
단어: title, 뜻: rich_text, 예문: rich_text, 숙달도: select(학습중/복습/완료), 복습일: date

## Views
1. table (default) - 전체 단어 목록 및 필터링
2. gallery - 단어 카드 뷰
3. board - 숙달도별 칸반 보드

## Block Pattern
heading("단어장") → callout(오늘의 단어) → database(inline) → divider → toggle(복습 스케줄) → quote(언어는 세계의 문)

## Color Theme
blue + green | cover: study
