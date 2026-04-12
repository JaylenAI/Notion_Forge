---
name: bookmark
parent: organize
description: 웹 북마크 카테고리별 정리 및 태그 관리
keywords: 북마크, 링크, 즐겨찾기, bookmark, link, favorite, web, resource
layout: sidebar_main
---
## DB Properties (required)
제목: title, URL: url, 카테고리: select(개발/디자인/마케팅/참고/도구), 태그: multi_select, 설명: rich_text, 추가일: date

## Views
1. table (default) - 전체 북마크 목록 및 필터링
2. gallery - 카드형 미리보기
3. list - 간단한 리스트 뷰

## Block Pattern
heading("북마크 관리") → callout(즐겨찾기 Top 5) → database(inline) → divider → toggle(카테고리 가이드) → toggle(정리 규칙)

## Color Theme
blue + gray | cover: tech
