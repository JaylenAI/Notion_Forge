---
name: sales
parent: crm
description: 영업 기회 파이프라인 및 매출 추적 대시보드
keywords: 영업, 세일즈, CRM, 파이프라인, sales, pipeline, deal, revenue
layout: dashboard_widgets
---
## DB Properties (required)
기회명: title, 고객: rich_text, 단계: select(리드/제안/협상/계약/완료), 금액: number, 확률: number, 마감일: date, 담당자: rich_text

## Views
1. board (default) - 단계별 파이프라인 보드
2. table - 전체 기회 목록 및 금액 합계
3. chart - 단계별 매출 분석
4. timeline - 마감일 기준 타임라인

## Block Pattern
heading("세일즈 파이프라인") → callout(이번 분기 목표) → database(inline) → divider → toggle(고객 분석) → toggle(성과 리포트)

## Color Theme
blue + orange | cover: business
