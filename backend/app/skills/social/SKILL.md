---
name: social
parent: content
description: SNS 콘텐츠 캘린더 및 플랫폼별 관리
keywords: SNS, 소셜미디어, 인스타, 틱톡, 트위터, social, media, instagram, tiktok
layout: calendar_main
---
## DB Properties (required)
콘텐츠: title, 플랫폼: multi_select(인스타/틱톡/트위터/페이스북/링크드인), 유형: select(이미지/영상/텍스트/스토리/릴스), 예정일: date, 해시태그: rich_text, 상태: status, 좋아요: number

## Views
1. table (default) - 전체 콘텐츠 목록
2. calendar - 발행 일정 캘린더
3. board - 상태별 콘텐츠 보드

## Block Pattern
heading("SNS 캘린더") → callout(이번 주 발행 계획) → database(inline) → divider → toggle(플랫폼별 가이드) → toggle(해시태그 모음)

## Color Theme
purple + pink | cover: social
