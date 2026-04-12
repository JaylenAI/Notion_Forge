---
name: subscription
parent: finance
description: 구독 서비스 결제 관리 및 상태 추적
keywords: 구독, 결제, 구독료, subscription, payment, recurring, service
layout: simple_tracker
---
## DB Properties (required)
서비스: title, 금액: number, 결제일: date, 카테고리: select(엔터/생산성/교육/기타), 상태: select(활성/해지예정/해지), 메모: rich_text

## Views
1. table (default) - 전체 구독 목록 및 월 합계
2. calendar - 결제일 캘린더

## Block Pattern
heading("구독 관리") → callout(월 구독료 합계) → database(inline) → divider → toggle(해지 검토) → toggle(무료 대안)

## Color Theme
yellow + gray | cover: tech
