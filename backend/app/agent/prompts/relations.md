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