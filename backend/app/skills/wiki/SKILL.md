---
name: wiki
description: Creates team knowledge base templates for internal documentation, policies, and shared knowledge. Search-driven with gallery and table views.
---

# Wiki (위키/지식베이스)

Creates templates for team knowledge management including internal documentation, policy archives, tool guides, and shared team knowledge.

## Quick Start

1. **Identify wiki context**: What does the user want to document? (policies, procedures, tools, culture, FAQ)
2. **Design properties**: Always include select(category) + multi_select(tags) + date(updated). Add context-specific fields.
3. **Set layout**: Two-column (left 30% category nav / right 70% document DB)
4. **Add gallery view**: Essential for visual document browsing
5. **Generate samples**: 5+ documents across different categories with realistic data

## Template Structure

### Layout
Two-column (left 30% category navigation callouts / right 70% document database)

### Block Order
1. callout: Knowledge sharing motivation message (theme color, context icon)
2. column_list:
   - Column 1 (30%): Category overview callout + recent updates callout
   - Column 2 (70%): Main document content area
3. heading_1: Main title (theme color)
4. database_ref: Inline database here
5. divider
6. toggle: "Document writing guide" with template and formatting standards

### Database Design

Required properties (always include):
- title: Document title
- select: Category (정책/절차/도구가이드/문화/FAQ/기술문서)
- multi_select: Tags (searchable topic tags)
- rich_text: Author
- date: Last updated
- status: Status (초안/검토중/게시됨/보관)

Context-dependent properties (AI decides):
- select: Department (개발/디자인/마케팅/인사/전사)
- select: Audience (전직원/팀원/매니저/신입)
- rich_text: Summary/abstract
- url: Related link

### Views
- Required: gallery (PRIMARY - visual document card browsing)
- Optional: table (full document list with search and filter)

### Sub-Pages
- "문서 작성 가이드" (Writing Guide): Standards for creating and formatting wiki documents
- "카테고리 설명" (Category Descriptions): Definitions and scope of each document category
- "업데이트 로그" (Update Log): Recent changes and revision history

### Sample Data
Generate 5+ wiki documents across categories with realistic Korean corporate data.
Each item needs: relevant icon, category, tags, author, update date, and status.

## Content Adaptation Examples

**Company Wiki**: Properties → title, category(정책/절차/문화), department, author, status, tags, audience(전직원/팀별)
**Tech Documentation**: Properties → title, tech stack(multi_select), version, author, last tested date, difficulty(select)
**FAQ Knowledge Base**: Properties → question, category, answer summary(rich_text), views count(number), helpful(checkbox)
**Process Documentation**: Properties → process name, department, frequency(select), owner, last reviewed, version(number)

## Formatting Rules

- Callout icon should match context (📖 wiki, 📚 knowledge, 🔍 search, 📝 document)
- Gallery view is the PRIMARY view (visual browsing encourages discovery)
- Keep properties under 8 (searchability over complexity)
- Tags should be practical and commonly searched terms
- Summary callouts should show total documents, recent updates, and category counts

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±1 month
- Document titles: realistic Korean corporate wiki entries (휴가 사용 가이드, 코드 리뷰 절차, Slack 채널 규칙, 신입사원 필독 문서, 보안 정책 안내)
- Category values: spread across 정책, 절차, 도구가이드, 문화, FAQ
- Tags: realistic multi_select values (인사, 개발, 보안, 협업, 온보딩, 복리후생)
- Author: realistic Korean names (김민수, 이지현, 박서연, 최준혁, 정하은)
- Status: mostly 게시됨, 1-2 초안 or 검토중

## Pro Design Guide

### Color Palette
- Primary: blue | Accent: purple | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 📚 전체 문서 수 (callout, purple_background)
  - 🆕 최근 업데이트 (callout, purple_background)
  - 📂 카테고리 수 (callout, purple_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "팀의 지식을 한곳에 모아 관리하세요! 함께 만드는 지식 허브 📖" (blue_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with gallery view (기본, 문서 카드), table view (전체 목록)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "library" (maps to themed Unsplash cover)
