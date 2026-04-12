---
name: sop
parent: guide
description: 표준 운영 절차(SOP) 관리
keywords: SOP, 절차, 매뉴얼, 프로세스, 운영, standard, operating, procedure
layout: sidebar_main
---
## DB Properties (required)
절차명: title, 부서: select(개발/디자인/마케팅/영업/인사), 빈도: select(매일/매주/매월/필요시), 담당자: rich_text, 최종검토일: date, 상태: status

## Views
1. table (default) - 전체 SOP 목록 및 부서별 필터링
2. board - 부서별 절차 상태 보드

## Block Pattern
heading("표준 운영 절차") → callout(SOP 관리 안내) → database(inline) → divider → toggle(절차 작성 가이드라인) → toggle(검토 주기 안내)

## Color Theme
gray + blue | cover: document
