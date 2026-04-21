---
name: blog
description: 블로그 콘텐츠 기획 및 발행 관리. SEO, 키워드, 조회수 트래킹까지 콘텐츠 파이프라인 전체를 관리.
---

# Blog (블로그/콘텐츠 관리)

Creates blog content management templates with editorial pipeline, SEO tracking, and publishing calendar. Full content workflow from ideation to publication.

## Quick Start

1. **Identify blog context**: What type of blog? Tech, lifestyle, review?
2. **Design properties**: Title + category + status + publish date + keywords + SEO score
3. **Set layout**: Two-column (Content Stats sidebar 25% + main pipeline 75%)
4. **Add board view**: Kanban pipeline is essential for content workflow
5. **Generate samples**: 5 realistic blog post entries with Korean context

## Template Structure

### Layout
Two-column: left 25% (Content Stats + Quick Links) / right 75% (pipeline area)

### Block Order
1. callout: Welcome message (blue_background, 📝)
2. divider
3. column_list:
   - left column:
     - heading_2: "콘텐츠 현황"
     - callout: "총 글 수" (blue_background, 📊)
     - callout: "이번 달 발행" (blue_background, 📅)
     - divider
     - heading_2: "리소스"
     - link_to_page: sub-page 1
     - link_to_page: sub-page 2
   - right column:
     - heading_1: Template title (blue)
     - callout: "콘텐츠 파이프라인을 관리하세요" (👇, blue_background)
4. divider
5. database_ref: Inline database here
6. divider
7. toggle: SEO 체크리스트
8. toggle: 자주 묻는 질문

### Database Design

Required properties (always include):
- title: 글 제목
- select: 카테고리 (기술/라이프/리뷰/튜토리얼/에세이)
- status: 상태 (아이디어/작성중/리뷰/발행완료)
- date: 발행일
- multi_select: 키워드
- number: SEO 점수 (0-100)
- number: 조회수
- rich_text: 요약
- url: 발행 URL
- select: 플랫폼 (티스토리/벨로그/미디엄/워드프레스/브런치)
- checkbox: 썸네일 완성

### Views
- Required: board (상태별 칸반 파이프라인)
- Optional: table (전체 글 목록), calendar (발행 일정)

### Sub-Pages
Generate 2 sub-pages:
- "🔍 SEO 가이드 & 키워드 리서치" — SEO 최적화 팁과 키워드 모음
- "📐 글쓰기 템플릿" — 카테고리별 글쓰기 구조 템플릿

### Sample Data
Generate 5 blog posts with realistic Korean blog topics.
Each post: unique category, varied statuses in pipeline, realistic SEO scores and view counts.

## Content Adaptation Examples

**기술 블로그**: Properties → 프로그래밍 언어, 난이도, 코드 포함 여부, GitHub 링크
**라이프 블로그**: Properties → 테마(일상/맛집/여행), 사진 수, 협찬 여부
**리뷰 블로그**: Properties → 제품명, 별점, 구매 링크, 제공 여부
**뉴스레터**: Properties → 발송일, 구독자 수, 오픈율, 클릭률
**브런치 작가**: Properties → 매거진, 글감 상태, 에디터 픽 여부, 좋아요 수
**기업 블로그**: Properties → 승인 상태, 작성자, 부서, 브랜드 가이드 준수

## Formatting Rules

- Board view should be the DEFAULT view (pipeline workflow first)
- Icon should match blog context (📝✍️🖊️📰💻)
- Sub-pages should have relevant icons
- Callout text should be creative and motivating

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within +/-2 weeks
- Status values: spread across all statuses (아이디어, 작성중, 리뷰, 발행완료)
- Select values: use different options for variety
- Number values: use realistic, varied numbers (SEO 0-100, 조회수 100-10000)
- Checkbox: mix of true and false

## Pro Design Guide

### Color Palette
- Primary: blue | Accent: gray | Secondary: blue
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 📝 총 글 수 (callout, gray_background)
  - 📅 이번 달 발행 (callout, gray_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "꾸준한 글쓰기가 최고의 브랜딩입니다. 콘텐츠를 관리하세요 📝" (blue_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with board view (기본, 파이프라인), table view (상세), calendar view (일정)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 SEO 체크리스트" with optimization tips
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "writing" (maps to themed Unsplash cover)
