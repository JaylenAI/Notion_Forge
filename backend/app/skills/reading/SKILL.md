---
name: reading
parent: collect
description: 독서 기록 및 평점 관리 컬렉션
keywords: 독서, 책, 서평, 평점, reading, book, review, library
layout: gallery_hero
---
## DB Properties (required)
책제목: title, 저자: rich_text, 장르: select(소설/자기계발/기술/에세이/역사), 상태: status, 평점: number, 날짜: date

## Views
1. gallery (default) - 책 표지 갤러리 뷰
2. table - 전체 목록 및 필터링
3. calendar - 독서 일정 관리

## Block Pattern
heading("독서 기록") → callout(올해 독서 목표) → database(inline) → divider → toggle(읽고 싶은 책) → quote(독서 명언)

## Color Theme
green + blue | cover: study
