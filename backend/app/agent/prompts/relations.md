## RELATION + ROLLUP + FORMULA (Mini-ERP)
When user requests interconnected databases (project+task, CRM, ERP), use relations:

### Relation Property:
In db_properties, use: "관련 프로젝트": {{"type": "relation", "target_db_index": 0}}
- target_db_index refers to the index in the databases[] array
- After creation, the system auto-links to the actual database ID

### Rollup Property (aggregates from related DB):
"총 태스크": {{"type": "rollup", "relation_property": "관련 프로젝트", "target_property": "이름", "function": "count"}}
- relation_property: name of the relation property in THIS database
- target_property: name of property to aggregate from RELATED database
- function: count, count_values, unique, sum, average, min, max, percent_empty, percent_not_empty, show_original

### Formula Property (calculated fields):
"D-Day": {{"type": "formula", "expression": "dateBetween(prop(\"마감일\"), now(), \"days\")"}}
"진행률": {{"type": "formula", "expression": "if(prop(\"상태\") == \"완료\", 100, if(prop(\"상태\") == \"진행 중\", 50, 0))"}}
"총액": {{"type": "formula", "expression": "prop(\"단가\") * prop(\"수량\")"}}

### Common Formula Patterns:
- D-Day countdown: dateBetween(prop("마감일"), now(), "days")
- Progress %: if(prop("상태") == "완료", 100, if(prop("상태") == "진행 중", 50, 0))
- Total: prop("단가") * prop("수량")
- Full name: prop("성") + " " + prop("이름")
- Status emoji: if(prop("완료"), "✅", "⬜")
- Overdue check: if(prop("마감일") < now(), "⚠️ 지연", "정상")

### Multi-DB Template Patterns:
1. Project + Task: Project DB has tasks via relation, rollup counts tasks per project
2. CRM: Contact DB + Deal DB + Activity DB, all linked via relation
3. Inventory: Product DB + Order DB, formula calculates total, rollup sums orders
4. School: Student DB + Assignment DB + Grade DB with rollup averages

### CRITICAL — Linking sample_items so rollups actually aggregate:
A rollup shows 0 (empty) unless its relation is filled with real sample links.
In sample_items, set the relation property to the EXACT title string(s) of item(s)
that you ALSO defined in the TARGET database's sample_items.
- Use the target item's title text — NOT an index, NOT an object. Just the string.
- For multiple links use an array of title strings.
- The TARGET titles MUST exist verbatim in the target DB's sample_items.

Example (CRM — 딜 belongs to 고객, 고객's 총거래액 rollup sums linked 딜 금액):
  databases[0] = 고객 (title "고객명"), rollup "총거래액" over relation "거래목록"
  databases[1] = 거래 (title "거래명"), relation "고객" → target_db_index 0
  databases[1].sample_items:
    {{"거래명": "엔터프라이즈 계약", "금액": 50000000, "고객": "삼성전자"}},
    {{"거래명": "연간 구독", "금액": 30000000, "고객": "삼성전자"}}
  databases[0].sample_items:
    {{"고객명": "삼성전자", ...}}   ← 거래.고객 값과 정확히 일치해야 링크됨
The system fills BOTH directions automatically, so 고객 "삼성전자"의 총거래액 = 80000000.
Spread links so at least one parent has 2+ children (demonstrates real aggregation).