---
name: wiki
parent: guide
description: 팀 지식 베이스 및 내부 위키
keywords: 위키, 지식, 문서, 사내, wiki, knowledge, base, documentation
layout: category_hub
---
## DB Properties (required)
제목: title, 카테고리: select(정책/절차/도구/문화), 작성자: rich_text, 태그: multi_select, 최종수정일: date, 상태: status

## Views
1. table (default) - 전체 문서 목록 및 검색
2. gallery - 카테고리별 문서 카드 갤러리

## Block Pattern
heading("팀 위키") → callout(지식 공유의 시작) → database(inline) → divider → toggle(문서 작성 가이드) → toggle(카테고리 설명)

## Color Theme
blue + purple | cover: library
