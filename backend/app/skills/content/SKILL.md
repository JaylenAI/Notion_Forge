---
name: content
description: Creates content planning templates for social media, blogs, YouTube, and editorial calendars. Status-driven with board and calendar views.
---

# Content (콘텐츠 기획)

Creates templates for content planning and management including social media calendars, blog management, YouTube planning, and editorial workflows.

## Quick Start

1. **Identify content context**: What does the user want to plan? (social media, blog, YouTube, newsletter)
2. **Design properties**: Always include status + date(publish) + select(platform). Add context-specific fields.
3. **Set layout**: Single column (board-focused, pipeline style)
4. **Add board view**: Essential for kanban-style content workflow
5. **Generate samples**: 5 items across different platforms and statuses

## Template Structure

### Layout
Single column (board-focused, pipeline style)

### Block Order
1. callout: Content strategy overview message (theme color, context icon)
2. heading_2: This week's content plan
3. to_do: Content checklist (items to publish this week)
4. divider
5. heading_1: Main title (theme color)
6. database_ref: Inline database here
7. toggle: "Content guidelines and best practices" with instructions

### Database Design

Required properties (always include):
- title: Content title
- status: Workflow stage (아이디어/작성중/리뷰/발행완료)
- date: Publish date
- select: Platform (블로그/인스타/유튜브/틱톡/트위터)

Context-dependent properties (AI decides):
- rich_text: Description/brief
- multi_select: Tags/hashtags
- url: Published link
- select: Content type (이미지/영상/글/릴스/쇼츠)
- select: Priority (높음/보통/낮음)

### Views
- Required: board (PRIMARY - kanban by status for workflow management)
- Optional: calendar (publishing schedule overview)

### Sub-Pages
- "콘텐츠 아이디어 뱅크" (Content Idea Bank): Collection of content ideas and inspiration
- "레퍼런스 모음" (Reference Collection): Links and examples of reference content

### Sample Data
Generate 5 content items across different platforms and at various workflow stages.
Each item needs: relevant icon, status, platform, publish date, and description.

## Content Adaptation Examples

**Blog**: Properties → topic, status, SEO keywords(multi_select), word count(number), draft link(url)
**YouTube**: Properties → video title, status(scripting/filming/editing/uploaded), duration, thumbnail status, script(rich_text)
**Instagram**: Properties → caption, type(reels/stories/carousel), hashtags(multi_select), collab partner, engagement goal
**Newsletter**: Properties → subject line, status, audience segment, send date, open rate target(number)

## Formatting Rules

- Callout icon should match context (📱 social media, ✍️ blog, 🎬 YouTube, 📧 newsletter)
- Board view is the PRIMARY view (content workflow is pipeline-based)
- Keep properties under 8 (content planning should be actionable, not overwhelming)
- Status options should reflect a clear content pipeline progression
- Sample items should span the full pipeline (some ideas, some in progress, some published)

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±2 weeks (mix of past published and future planned)
- Status values: spread across all statuses (아이디어, 작성중, 리뷰, 발행완료)
- Platform values: use different platforms for variety (블로그, 인스타, 유튜브, 틱톡, 트위터)
- Content type: mix of 이미지, 영상, 글, 릴스, 쇼츠
- Description: realistic Korean content briefs (봄맞이 카페 추천 리스트, 주간 개발 회고 블로그, etc.)
- Tags: relevant hashtags per platform

## Pro Design Guide

### Color Palette
- Primary: purple | Accent: orange | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 📝 초안 (callout, orange_background)
  - 📤 발행 예정 (callout, orange_background)
  - ✅ 발행 완료 (callout, orange_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "콘텐츠 파이프라인을 한눈에 관리하세요! 아이디어에서 발행까지 📱" (purple_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with board view (기본, 상태별 칸반), calendar view (발행 일정)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "creative" (maps to themed Unsplash cover)
