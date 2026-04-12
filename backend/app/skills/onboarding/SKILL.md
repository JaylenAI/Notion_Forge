---
name: onboarding
parent: guide
description: 신입사원 온보딩 가이드 및 체크리스트
keywords: 온보딩, 신입, 입사, 교육, 체크리스트, onboarding, new hire, orientation
layout: category_hub
---
## DB Properties (required)
단계명: title, 카테고리: select(IT설정/조직소개/업무교육/복리후생), 담당자: rich_text, 기한: date, 완료: checkbox, 메모: rich_text

## Views
1. table (default) - 전체 온보딩 단계 목록 및 진행 현황
2. board - 카테고리별 그룹 상태 보드

## Block Pattern
heading("신입사원 온보딩 가이드") → callout(환영 메시지) → database(inline) → divider → toggle(부서별 안내) → toggle(자주 묻는 질문)

## Color Theme
blue + green | cover: office
