---
name: contact
parent: organize
description: 연락처 관리 및 그룹별 정리 갤러리
keywords: 연락처, 주소록, 인맥, contact, address, people, network
layout: gallery_hero
---
## DB Properties (required)
이름: title, 전화: rich_text, 이메일: email, 회사: rich_text, 그룹: select(업무/개인/가족), 메모: rich_text

## Views
1. gallery (default) - 프로필 카드 갤러리
2. table - 전체 연락처 목록
3. list - 간단한 리스트 뷰

## Block Pattern
heading("연락처 관리") → callout(자주 연락하는 사람) → database(inline) → divider → toggle(그룹별 정리) → toggle(명함 스캔)

## Color Theme
blue + green | cover: business
