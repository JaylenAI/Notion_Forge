---
name: investment
parent: finance
description: 투자 포트폴리오 및 수익률 추적 대시보드
keywords: 투자, 주식, ETF, 수익률, investment, stock, portfolio, return
layout: dashboard_widgets
---
## DB Properties (required)
종목: title, 매수가: number, 수량: number, 현재가: number, 수익률: formula, 카테고리: select(주식/ETF/펀드/코인), 매수일: date

## Views
1. table (default) - 전체 포트폴리오 및 수익률
2. chart - 카테고리별 투자 비중 차트

## Block Pattern
heading("투자 대시보드") → callout(포트폴리오 요약) → database(inline) → divider → toggle(투자 원칙) → toggle(리밸런싱 기록)

## Color Theme
green + blue | cover: finance
