---
name: life_os
parent: hub
description: 라이프 OS 개인 대시보드 및 영역별 목표 관리
keywords: 라이프, 인생, 대시보드, 자기관리, life, os, personal, dashboard
layout: dashboard_widgets
---
## DB Properties (required)
영역: title, 카테고리: select(건강/관계/재정/커리어/자기계발/취미), 목표: rich_text, 진행률: number, 다음행동: rich_text, 상태: status

## Views
1. table (default) - 전체 영역 목록 및 진행률 확인
2. board - 상태별 영역 보드
3. gallery - 영역별 카드 갤러리

## Block Pattern
heading("Life OS") → callout(나의 인생 대시보드) → database(inline) → divider → toggle(영역별 목표 설정 가이드) → toggle(주간 리뷰 체크리스트)

## Color Theme
purple + blue | cover: lifestyle
