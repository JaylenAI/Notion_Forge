---
name: meeting
description: 회의록 자동 생성 — 안건, 결정사항, 액션아이템 포함
keywords: 회의,미팅,회의록,안건,meeting,minutes,agenda
---

# Meeting Notes

회의록 템플릿을 만듭니다.

## Template Structure

### Layout
Single column

### Block Order
1. callout: 회의 정보 (날짜, 참석자)
2. heading_1: 안건
3. numbered_list: 안건 목록
4. heading_1: 결정사항
5. bulleted_list: 결정 목록
6. heading_1: 액션 아이템
7. database_ref: 액션 아이템 DB
8. divider
9. toggle: 회의 가이드

## Database Properties
- 액션: title
- 담당자: rich_text
- 마감일: date
- 상태: status
- 우선순위: select (높음/중간/낮음)

## Views
- table (기본)
- board (상태별)

## Sample Data
5개 이상의 현실적인 액션 아이템
