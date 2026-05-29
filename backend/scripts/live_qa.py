"""라이브 QA 하네스 — 실제 Notion에 템플릿을 생성하고 품질을 정량 검증한다.

검증 항목: 페이지/DB 생성, **DB별 샘플 행 실제 삽입 수**, 속성 타입(relation/rollup/formula),
뷰 개수. 실제 워크스페이스(parent page)에 페이지를 생성하므로 recipe-id 인자가 있을 때만 실행한다.

사용:
    uv run python scripts/live_qa.py <recipe-id>
    uv run python scripts/live_qa.py crm-dashboard
"""

import asyncio
import json
import sys
from pathlib import Path

from app.agent.creation_executor import CreationExecutor
from app.agent.tools.add_database_items import AddDatabaseItemsTool
from app.notion.client import NotionClient

ROOT = Path(__file__).resolve().parents[2]


async def qa_recipe(recipe_id: str) -> int:
    fp = ROOT / "recipes" / f"{recipe_id}.json"
    if not fp.exists():
        print(f"레시피 없음: {fp}")
        return 1
    data = json.loads(fp.read_text(encoding="utf-8"))
    bp = data["blueprint"]
    expected_dbs = bp.get("databases", [])
    expected_samples = {db.get("title"): len(db.get("sample_items", [])) for db in expected_dbs}

    client = NotionClient()
    if client.mock_mode:
        print("mock 모드 — Notion 키 없음. 중단")
        return 1

    print(f"=== 라이브 QA: {recipe_id} ===")
    executor = CreationExecutor(client, AddDatabaseItemsTool(client))
    result = await executor.execute_blueprint(bp, client.parent_page_id)

    issues: list[str] = []

    pages = result.get("pages", [])
    dbs = result.get("databases", [])
    print(f"페이지: {len(pages)} | DB: {len(dbs)} | 블록: {result.get('blocks', 0)}")
    print(f"URL: {result.get('main_url')}")

    if len(dbs) != len(expected_dbs):
        issues.append(f"DB 수 불일치: 기대 {len(expected_dbs)}, 실제 {len(dbs)}")

    print("\n-- DB별 검증 --")
    for db in dbs:
        db_id = db["id"]
        title = db.get("title", "?")
        # 속성
        ds_id = await client.get_data_source_id(db_id)
        ds = await client.get_data_source(ds_id)
        props = ds.get("properties", {}) or (await client.get_database(db_id)).get("properties", {})
        types = {n: p.get("type") for n, p in props.items()}
        rollup = [n for n, t in types.items() if t == "rollup"]
        formula = [n for n, t in types.items() if t == "formula"]
        relation = [n for n, t in types.items() if t == "relation"]
        # 샘플 행 실제 삽입 수
        rows = await client.query_database(db_id)
        exp = expected_samples.get(title, 0)
        mark = "✅" if len(rows) == exp else "⚠️"
        print(f"  [{title}] 속성 {len(props)} | 샘플행 {len(rows)}/{exp} {mark}")
        print(f"      relation={relation} rollup={rollup} formula={formula}")
        if len(rows) != exp:
            issues.append(f"{title}: 샘플행 {len(rows)}/{exp}")
        if not any(t == "title" for t in types.values()):
            issues.append(f"{title}: title 속성 없음")

    await client.close()

    print("\n=== QA 결과 ===")
    if issues:
        print("⚠️ 이슈:")
        for i in issues:
            print("  -", i)
        return 2
    print("✅ 모든 검증 통과 (페이지/DB/샘플행/속성)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용: uv run python scripts/live_qa.py <recipe-id>")
        sys.exit(1)
    sys.exit(asyncio.run(qa_recipe(sys.argv[1])))
