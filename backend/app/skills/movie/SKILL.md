---
name: movie
parent: collect
description: 영화/드라마 감상 기록 및 평점 관리
keywords: 영화, 드라마, 넷플릭스, 평점, movie, film, drama, netflix, review
layout: gallery_hero
---
## DB Properties (required)
제목: title, 장르: select(액션/드라마/코미디/SF/호러/로맨스), 플랫폼: select(넷플릭스/디즈니+/왓챠/극장), 평점: number, 상태: status, 감상일: date

## Views
1. gallery (default) - 포스터 갤러리 뷰
2. table - 전체 감상 목록
3. board - 상태별 칸반 보드

## Block Pattern
heading("영화 기록") → callout(이번 달 추천작) → database(inline) → divider → toggle(보고 싶은 리스트) → quote(영화 명대사)

## Color Theme
red + gray | cover: creative
