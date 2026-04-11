## VIEW CATALOG — Choose what fits the user's intent

Each database has a "views" array. Each view is an object with "type", "title", and optional configuration fields.
The system will pass ALL fields you specify directly to the Notion Views API.
Choose views that MAKE SENSE for the user's request — don't add views just to fill a quota.

### Available view types and their configuration options:

**table** — Default spreadsheet view. Good for data-heavy use cases.
  {{"type": "table", "title": "전체 목록", "wrap_cells": true, "frozen_column_index": 1}}

**board** — Kanban columns. Best when DB has status/select property.
  {{"type": "board", "title": "상태별", "group_by": {{"property": "상태"}},
    "cover": {{"type": "page_cover"}}, "cover_size": "medium", "cover_aspect": "cover", "card_layout": "compact"}}
  - cover options: {{"type":"page_cover"}}, {{"type":"page_content"}}, or {{"type":"property","property_id":"FILES_PROP"}}
  - cover_size: "small" | "medium" | "large"

**gallery** — Visual card grid. Great for portfolios, contacts, recipes, collections.
  {{"type": "gallery", "title": "갤러리", "cover": {{"type": "page_cover"}}, "cover_size": "medium", "cover_aspect": "cover"}}

**calendar** — Date-based layout. Use when DB has a date property.
  {{"type": "calendar", "title": "일정", "date_property": "날짜", "show_weekends": true}}

**timeline** — Gantt chart. Best for projects with start/end dates.
  {{"type": "timeline", "title": "타임라인", "date_property": "시작일", "end_date_property_id": "마감일",
    "zoom_level": "month", "arrows_by": {{"property_id": "RELATION_PROP"}} }}

**chart** — Data visualization. Great for tracking, analytics, summaries.
  {{"type": "chart", "title": "통계", "chart_type": "donut",
    "x_axis": {{"property": "상태"}}, "color_theme": "blue", "show_data_labels": true, "height": "medium"}}
  - chart_type: "column" | "bar" | "line" | "donut" | "number"
  - color_theme: "gray" | "blue" | "yellow" | "green" | "purple" | "teal" | "orange" | "pink" | "red" | "colorful"

**list** — Minimal row list. Good for simple reference/lookup.
  {{"type": "list", "title": "리스트"}}

**form** — Data collection from external users.
  {{"type": "form", "title": "응답 폼", "anonymous_submissions": true}}

### When to use which views (guidelines, not rules):
- Status/workflow tracking → board (group by status) + table
- Date-heavy data → calendar + table
- Visual content (portfolio/contacts) → gallery + table
- Project management → board + timeline + calendar
- Analytics/dashboard → chart + table
- Simple tracker → table only is fine
- Complex system → pick 3-4 that genuinely help the user

### linked_view for dashboard widgets:
When building dashboards, use linked_view blocks to show FILTERED slices of the same DB:
  {{"type": "linked_view", "db_index": 0, "view_type": "list", "title": "이번주 할일",
    "filter": {{"property": "날짜", "date": {{"this_week": {{}} }} }} }}
This is powerful for at-a-glance summaries. Use when it genuinely helps — not as decoration.