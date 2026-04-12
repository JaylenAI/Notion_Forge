---
name: youtube
parent: content
description: 유튜브 콘텐츠 기획 및 제작 관리
keywords: 유튜브, 영상, 촬영, 편집, 썸네일, youtube, video, creator, vlog
layout: kanban_board
---
## DB Properties (required)
영상제목: title, 카테고리: select(브이로그/튜토리얼/리뷰/쇼츠/라이브), 상태: status, 촬영일: date, 스크립트: rich_text, 조회수: number, 썸네일상태: select(미완성/완성)

## Views
1. table (default) - 전체 영상 목록 및 제작 현황
2. board - 상태별 제작 파이프라인
3. calendar - 촬영 및 업로드 일정

## Block Pattern
heading("유튜브 관리") → callout(영상 제작 파이프라인) → database(inline) → divider → toggle(촬영 체크리스트) → toggle(썸네일 가이드)

## Color Theme
red + gray | cover: video
