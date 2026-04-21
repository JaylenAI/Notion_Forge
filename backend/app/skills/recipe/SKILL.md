---
name: recipe
description: Creates recipe collection templates with cuisine categorization, difficulty levels, cooking time, ingredient management, and visual gallery browsing.
---

# Recipe (레시피 수집)

Creates templates for collecting and organizing recipes with visual card browsing. Users save favorite recipes with ingredients, cooking steps, and personal ratings for a complete digital cookbook.

## Quick Start

1. **Identify recipe context**: What kind of cooking/recipes does the user collect?
2. **Design properties**: Title + cuisine + difficulty + cook time + rating + context fields
3. **Set layout**: Two-column (Quick Action sidebar 25% + main content 75%)
4. **Add gallery view**: Card-based food photo display is essential
5. **Generate samples**: 5 realistic Korean recipe names with full metadata

## Template Structure

### Layout
Two-column: left 25% (Quick Action + Menu) / right 75% (content area)

### Block Order
1. callout: Cooking inspiration message (orange_background, 🍳)
2. empty paragraph (whitespace)
3. column_list:
   - left column (30%):
     - callout: "📝 총 레시피 수" (green_background)
     - callout: "⭐ 베스트 레시피" (green_background)
   - right column (70%):
     - heading_2: Template title (orange)
     - callout: "나만의 레시피를 둘러보세요 👇" (orange_background)
4. divider
5. database_ref: Inline database here
6. empty paragraph (whitespace)
7. divider
8. toggle: "📖 사용 가이드" with numbered setup steps
9. toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Database Design

Required properties (always include):
- title: 요리 이름
- select: 카테고리 (한식/양식/중식/일식/디저트/음료)
- select: 난이도 (초보/보통/고급)
- number: 조리시간 (분)
- number: 평점 (1-5)
- date: 등록일

Context-dependent properties:
- rich_text: 재료 목록
- number: 인분 (servings)
- rich_text: 조리 팁/메모
- checkbox: 즐겨찾기
- multi_select: 태그 (초간단/도시락/손님접대/다이어트/아이반찬)
- url: 레시피 출처 (유튜브/블로그 링크)

### Views
- Required: gallery (음식 사진 갤러리)
- Optional: table (전체 레시피 목록 및 필터링), board (카테고리별 그룹)

### Sub-Pages
- 🛒 장보기 목록: Weekly grocery shopping list
- 📅 주간 식단표: Weekly meal planning calendar

### Sample Data rules
Generate 5 items with REAL Korean recipe names.
Each item: unique icon, varied cuisines, different difficulty levels, varied ratings.

## Content Adaptation Examples

**한식 레시피**: Properties → 종류(select: 찌개/볶음/구이/나물/국), 양념(rich_text), 조리시간(number), 난이도(select), 밑반찬여부(checkbox)
**베이킹**: Properties → 종류(select: 빵/케이크/쿠키/타르트), 오븐온도(number), 굽는시간(number), 특수도구(multi_select), 밀가루종류(select)
**칵테일/음료**: Properties → 베이스(select: 진/럼/보드카/위스키/논알콜), 재료(multi_select), 도수(number), 맛(select: 달콤/상큼/쓴맛/드라이)
**이유식/아기반찬**: Properties → 단계(select: 초기/중기/후기), 알레르기주의(multi_select), 보관방법(select), 보관기간(number/일)
**다이어트 레시피**: Properties → 칼로리(number), 단백질(number), 탄수화물(number), 식이섬유(number), GI지수(select)
**밀프렙/도시락**: Properties → 보관일수(number), 전자레인지(checkbox), 소분횟수(number), 예상비용(number)

## Formatting Rules

- Gallery view should be the DEFAULT view (visual food browsing)
- Icon should be 🍳 or food-related (🥘🍰🍜🥗)
- Orange theme conveys warmth, appetite, and cooking energy
- Sub-pages should have relevant icons
- Callout text should be warm and inviting
- Cooking times should be in minutes (realistic: 10-120)

## Sample Data Requirements

EVERY generated template MUST include sample data with these rules:
- Minimum 5 sample items per database
- ALL property values must be filled (not just title and icon)
- Date values: use realistic dates within ±2 weeks
- Examples: "🥘 김치찌개" (카테고리: 한식, 난이도: 초보, 조리시간: 30, 평점: 5, 인분: 2, 즐겨찾기: true), "🍝 까르보나라" (카테고리: 양식, 난이도: 보통, 조리시간: 25, 평점: 4, 인분: 2, 즐겨찾기: true), "🍣 연어덮밥" (카테고리: 일식, 난이도: 초보, 조리시간: 15, 평점: 4, 인분: 1, 즐겨찾기: false), "🥮 마라탕" (카테고리: 중식, 난이도: 보통, 조리시간: 40, 평점: 5, 인분: 2, 즐겨찾기: true), "🍰 바스크 치즈케이크" (카테고리: 디저트, 난이도: 고급, 조리시간: 60, 평점: 5, 인분: 8, 즐겨찾기: true)
- Select values: spread across all cuisines and difficulties
- Number values: realistic cooking times

## Pro Design Guide

### Color Palette
- Primary: orange | Accent: green | Secondary: gray
- Apply primary to: callout backgrounds, heading colors, select options
- Apply accent to: stat callouts, highlight callouts only

### Dashboard Layout (REQUIRED)
Use column_list with 2 columns for every template:
- LEFT (30%): stat callouts
  - 📝 총 레시피 수 (callout, green_background)
  - ⭐ 베스트 레시피 (callout, green_background)
- RIGHT (70%): heading_2 + primary database_ref

### Must-Have Blocks
1. Welcome callout: "요리는 사랑입니다. 나만의 레시피북을 만들어보세요 🍳" (orange_background)
2. Empty paragraph (whitespace)
3. Column dashboard layout
4. Primary database with gallery view (기본), table view (상세)
5. Empty paragraph (whitespace)
6. Divider
7. Toggle: "📖 사용 가이드" with numbered setup steps
8. Toggle: "❓ 자주 묻는 질문" with 2-3 FAQs

### Cover Image Category
cover_category: "food" (maps to themed Unsplash cover)
