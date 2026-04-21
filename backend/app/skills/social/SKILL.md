---
name: social
description: SNS 콘텐츠 캘린더 및 플랫폼별 관리. 인스타, 틱톡, 트위터 등 멀티 플랫폼 소셜미디어 전략을 한눈에.
---

# Social (SNS/소셜미디어 관리)

Creates social media content calendar templates with multi-platform management, hashtag tracking, and engagement analytics. Unified dashboard for all social channels.

## Quick Start

1. **Identify social context**: Which platforms does the user manage?
2. **Design properties**: Content + platforms + type + scheduled date + hashtags + status + engagement
3. **Set layout**: Two-column (Social Stats sidebar 25% + content calendar 75%)
4. **Add calendar view**: Content scheduling calendar is essential
5. **Generate samples**: 5 realistic social media posts with Korean context

## Template Structure

### Layout
Two-column: left 25% (Social Stats + Quick Links) / right 75% (content calendar)

### Block Order
1. callout: Welcome message (purple_background, 📱)
2. divider
3. column_list:
   - left column:
     - heading_2: "소셜 현황"
     - callout: "이번 주 발행" (purple_background, 📊)
     - callout: "총 콘텐츠 수" (purple_background, 📈)
     - divider
     - heading_2: "리소스"
     - link_to_page: sub-page 1
     - link_to_page: sub-page 2
   - right column:
     - heading_1: Template title (purple)
     - callout: "소셜미디어 콘텐츠를 계획하세요" (👇, purple_background)
4. divider
5. database_ref: Inline database here
6. divider
7. toggle: 플랫폼별 최적화 가이드
8. toggle: 자주 묻는 질문

### Database Design

Required properties (always include):
- title: 콘텐츠 제목
- multi_select: 플랫폼 (인스타그램/틱톡/트위터/페이스북/링크드인/유튜브쇼츠)
- select: 유형 (이미지/영상/텍스트/스토리/릴스/캐러셀)
- date: 예정일
- rich_text: 해시태그
- status: 상태 (아이디어/제작중/승인대기/발행완료)
- number: 좋아요
- number: 도달 수
- rich_text: 캡션
- checkbox: 협찬/광고
- select: 시간대 (아침/점심/저녁/심야)

### Views
- Required: calendar (발행 일정 캘린더)
- Optional: board (상태별 콘텐츠 보드), table (전체 목록)

### Sub-Pages
Generate 2 sub-pages:
- "#️⃣ 해시태그 모음" — 카테고리별 인기 해시태그 정리
- "📐 플랫폼별 이미지 사이즈 가이드" — 각 플랫폼 최적 규격

### Sample Data
Generate 5 social media posts spanning different platforms.
Each post: unique platform mix, varied content types, realistic Korean social media content.

## Content Adaptation Examples

**인스타 크리에이터**: Properties → 피드/릴스/스토리, 필터, 촬영 장소, 태그 계정
**기업 SNS 관리자**: Properties → 브랜드 가이드 준수, 승인자, 캠페인명, 예산
**틱톡 크리에이터**: Properties → 트렌드 음원, 챌린지명, 듀엣 여부, 바이럴 점수
**링크드인 마케터**: Properties → 타겟 직군, CTA, 리드 수, 전환율
**개인 브랜딩**: Properties → 퍼스널 브랜드 키워드, 톤앤매너, 핵심 메시지
**쇼핑몰 SNS**: Properties → 상품명, 할인율, 링크, 매출 기여도

## Formatting Rules

- Calendar view should be the DEFAULT view (scheduling first)
- Icon should match social context (📱📸🎵🐦💬)
- Sub-pages should have relevant icons
- Callout text should be trendy and dynamic

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within +/-2 weeks
- Status values: spread across all statuses (아이디어, 제작중, 승인대기, 발행완료)
- Select values: use different options for variety
- Number values: use realistic, varied numbers (좋아요 50-5000, 도달 수 200-50000)
- Checkbox: mix of true and false

## Pro Design Guide

### Color Palette
- Primary: purple | Accent: pink | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 📱 이번 주 발행 (callout, pink_background)
  - 📈 총 콘텐츠 수 (callout, pink_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "소셜미디어를 전략적으로! 모든 플랫폼을 한 곳에서 관리하세요 📱" (purple_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with calendar view (기본, 일정), board view (상태별), table view (상세)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 플랫폼별 최적화 가이드" with platform-specific tips
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "social" (maps to themed Unsplash cover)
