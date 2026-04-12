---
name: blog
parent: content
description: 블로그 콘텐츠 기획 및 발행 관리
keywords: 블로그, 글쓰기, SEO, 발행, blog, writing, post, article
layout: kanban_board
---
## DB Properties (required)
제목: title, 카테고리: select(기술/라이프/리뷰/튜토리얼/에세이), 상태: status, 발행일: date, 키워드: multi_select, SEO점수: number, 조회수: number

## Views
1. table (default) - 전체 글 목록 및 SEO 현황
2. board - 상태별 칸반 보드
3. calendar - 발행 일정 캘린더

## Block Pattern
heading("블로그 관리") → callout(콘텐츠 파이프라인) → database(inline) → divider → toggle(SEO 체크리스트) → toggle(글쓰기 가이드)

## Color Theme
blue + gray | cover: writing
