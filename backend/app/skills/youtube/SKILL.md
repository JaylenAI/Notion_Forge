---
name: youtube
description: 유튜브 콘텐츠 기획 및 제작 관리. 촬영, 편집, 썸네일, 업로드까지 영상 제작 파이프라인 전체를 관리.
---

# YouTube (유튜브/영상 관리)

Creates YouTube content management templates with video production pipeline, thumbnail tracking, and upload calendar. Full workflow from ideation to publishing.

## Quick Start

1. **Identify channel context**: What type of YouTube channel? Vlog, tutorial, review?
2. **Design properties**: Title + category + status + filming date + script + views + thumbnail
3. **Set layout**: Two-column (Channel Stats sidebar 25% + production pipeline 75%)
4. **Add board view**: Kanban pipeline is essential for video production workflow
5. **Generate samples**: 5 realistic video entries with Korean YouTuber context

## Template Structure

### Layout
Two-column: left 25% (Channel Stats + Quick Links) / right 75% (production pipeline)

### Block Order
1. callout: Welcome message (red_background, 🎬)
2. divider
3. column_list:
   - left column:
     - heading_2: "채널 현황"
     - callout: "총 영상 수" (red_background, 📊)
     - callout: "이번 달 업로드" (red_background, 📅)
     - divider
     - heading_2: "리소스"
     - link_to_page: sub-page 1
     - link_to_page: sub-page 2
   - right column:
     - heading_1: Template title (red)
     - callout: "영상 제작 파이프라인을 관리하세요" (👇, red_background)
4. divider
5. database_ref: Inline database here
6. divider
7. toggle: 촬영 체크리스트
8. toggle: 자주 묻는 질문

### Database Design

Required properties (always include):
- title: 영상 제목
- select: 카테고리 (브이로그/튜토리얼/리뷰/쇼츠/라이브)
- status: 상태 (기획/촬영예정/촬영완료/편집중/업로드완료)
- date: 촬영일
- date: 업로드 예정일
- rich_text: 스크립트 요약
- number: 조회수
- select: 썸네일 상태 (미완성/완성)
- rich_text: 태그
- url: 영상 링크
- number: 영상 길이 (분)
- checkbox: 자막 완성

### Views
- Required: board (상태별 제작 파이프라인)
- Optional: table (전체 영상 목록), calendar (촬영 및 업로드 일정)

### Sub-Pages
Generate 2 sub-pages:
- "🎨 썸네일 가이드 & 레퍼런스" — 클릭률 높은 썸네일 패턴 모음
- "📋 촬영 체크리스트" — 촬영 전/중/후 확인사항

### Sample Data
Generate 5 video entries with realistic Korean YouTuber topics.
Each entry: unique category, varied production stages, realistic view counts.

## Content Adaptation Examples

**브이로그 채널**: Properties → 촬영 장소, 배경음악, 촬영 장비, 분위기
**기술 튜토리얼**: Properties → 프로그래밍 언어, 난이도, 코드 리포, 챕터 구성
**먹방/쿡방**: Properties → 메뉴, 재료비, 조리시간, 난이도, 레시피 링크
**게임 채널**: Properties → 게임명, 장르, 녹화 시간, 하이라이트 구간
**교육 채널**: Properties → 과목, 학습 목표, 자료 링크, 퀴즈 포함 여부
**쇼츠 전문**: Properties → 원본 영상, 편집 포인트, 후킹 멘트, 해시태그

## Formatting Rules

- Board view should be the DEFAULT view (production pipeline first)
- Icon should match YouTube context (🎬🎥📹🔴▶️)
- Sub-pages should have relevant icons
- Callout text should be energetic and creative

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within +/-2 weeks
- Status values: spread across all statuses (기획, 촬영예정, 촬영완료, 편집중, 업로드완료)
- Select values: use different options for variety
- Number values: use realistic, varied numbers (조회수 500-100000, 영상길이 1-60)
- Checkbox: mix of true and false

## Pro Design Guide

### Color Palette
- Primary: red | Accent: gray | Secondary: red
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 🎬 총 영상 수 (callout, gray_background)
  - 📅 이번 달 업로드 (callout, gray_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "크리에이터의 모든 것을 관리하세요! 영상 제작이 쉬워집니다 🎬" (red_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with board view (기본, 파이프라인), table view (상세), calendar view (일정)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 촬영 & 편집 체크리스트" with production tips
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "video" (maps to themed Unsplash cover)
