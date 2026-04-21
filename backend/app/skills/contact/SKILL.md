---
name: contact
description: Creates contact and address book management templates for people tracking, group organization, and networking. Gallery-driven with table and list views.
---

# Contact (연락처 관리)

Creates templates for contact management including address book organization, group categorization, networking notes, and relationship tracking.

## Quick Start

1. **Identify contact context**: What contacts to manage? (business, personal, clients, networking, family)
2. **Design properties**: Always include email + rich_text(phone) + select(group). Add context-specific fields.
3. **Set layout**: Two-column (left 25% group summary / right 75% contact DB)
4. **Add gallery view**: Essential for visual people-card browsing
5. **Generate samples**: 5 contacts across different groups with realistic Korean contact data

## Template Structure

### Layout
Two-column (left 25% group stats / right 75% contact gallery database)

### Block Order
1. callout: Contact management intro message (theme color, context icon)
2. column_list:
   - Column 1 (25%): Total contacts callout + recently added callout
   - Column 2 (75%): Main contact content area
3. divider
4. heading_1: Main title (theme color)
5. database_ref: Inline database here
6. toggle: "연락처 관리 팁" with organization best practices and networking tips

### Database Design

Required properties (always include):
- title: Person name
- email: Contact email
- rich_text: Phone number
- select: Group (업무/개인/가족/거래처/네트워킹)

Context-dependent properties (AI decides):
- rich_text: Company/organization
- rich_text: Position/title
- rich_text: Address
- date: Birthday
- date: Last contacted
- multi_select: Tags (동창/프로젝트/세미나/소개)
- select: Relationship (친밀/보통/비즈니스/신규)
- rich_text: Notes/memo
- url: LinkedIn or social profile
- checkbox: Favorites/starred

### Views
- Required: gallery (PRIMARY - visual people cards for quick recognition)
- Optional: table (all contact details in spreadsheet)
- Optional: list (compact alphabetical directory)
- Optional: board (grouped by relationship or group)

### Sub-Pages
- "명함 보관함" (Business Card Archive): Scanned or noted business card information
- "네트워킹 로그" (Networking Log): Records of meetings, events, and follow-up notes

### Sample Data
Generate 5 contacts across different groups with realistic Korean personal/business data.
Each item needs: relevant icon, group, company, phone, email, and notes.

## Content Adaptation Examples

**Business Contacts**: Properties → company, position, department, deal status(select), last meeting date, referral source
**Personal Address Book**: Properties → group(친구/가족/이웃), birthday, anniversary, address, relationship, gift ideas(rich_text)
**Client Directory**: Properties → company, contract value, renewal date, account manager, satisfaction(1-5), industry
**Networking Contacts**: Properties → met at(event name), date met, mutual connections, follow-up status, interest areas(multi_select)
**Team Directory**: Properties → department, role, skills(multi_select), office location, start date, manager

## Formatting Rules

- Callout icon should match context (👤 general, 💼 business, 👨‍👩‍👧 family, 🤝 networking)
- Gallery view is the PRIMARY view (visual recognition is key for contacts)
- Keep properties under 9 (contacts need key info at a glance)
- Phone format should follow Korean convention (010-XXXX-XXXX)
- Quick stats callout should show key metrics (total contacts, by group, recently added)

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic birthdays and last-contacted dates
- Group values: spread across options (업무, 개인, 가족, 거래처, 네트워킹)
- Phone: realistic Korean phone numbers (010-1234-5678, 010-9876-5432)
- Email: realistic Korean email formats (hong.gildong@company.co.kr, kim.minjun@gmail.com)
- Company: realistic Korean company names (삼성전자, 네이버, 카카오, LG전자, 현대자동차)
- Names: realistic Korean names (홍길동, 김민준, 이서연, 박지호, 정수빈)
- Position: realistic Korean positions (대리, 과장, 팀장, 부장, 이사, 대표)

## Pro Design Guide

### Color Palette
- Primary: blue | Accent: green | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 👥 전체 연락처 (callout, green_background)
  - 💼 업무 연락처 (callout, green_background)
  - 🆕 최근 추가 (callout, green_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "소중한 인연을 체계적으로! 모든 연락처를 한곳에서 관리하세요 👥" (blue_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with gallery view (기본, 프로필 카드), table view (상세), list view (디렉토리)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "business" (maps to themed Unsplash cover)
