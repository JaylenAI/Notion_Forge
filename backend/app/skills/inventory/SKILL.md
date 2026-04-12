---
name: inventory
parent: organize
description: 물품 재고 관리 및 위치/카테고리별 정리
keywords: 재고, 물품, 자산, 관리, inventory, asset, stock, management
layout: sidebar_main
---
## DB Properties (required)
물품명: title, 수량: number, 위치: rich_text, 카테고리: select(전자기기/사무용품/가구/기타), 구매일: date, 가격: number

## Views
1. table (default) - 전체 물품 목록 및 수량 확인
2. board - 카테고리별 물품 보드

## Block Pattern
heading("물품 관리") → callout(재고 현황 요약) → database(inline) → divider → toggle(구매 요청) → toggle(폐기 목록)

## Color Theme
gray + blue | cover: business
