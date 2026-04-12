---
name: music
parent: collect
description: 음악 플레이리스트 및 분위기별 정리
keywords: 음악, 노래, 플레이리스트, music, song, playlist, artist
layout: gallery_hero
---
## DB Properties (required)
곡명: title, 아티스트: rich_text, 장르: select, 분위기: multi_select(신나는/잔잔한/우울한/에너지), 평점: number

## Views
1. gallery (default) - 앨범 커버 갤러리
2. table - 전체 곡 목록 및 필터링

## Block Pattern
heading("음악 라이브러리") → callout(이번 주 추천곡) → database(inline) → divider → toggle(플레이리스트) → quote(음악 명언)

## Color Theme
purple + pink | cover: creative
