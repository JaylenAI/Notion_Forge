"""라이브 QA 하네스 — 실제 Notion에 템플릿을 생성하고 품질을 정량 검증한다.

검증: 페이지/DB 생성, DB별 샘플 행 실제 삽입 수, 속성 타입(relation/rollup/formula).
실제 워크스페이스(parent page)에 페이지를 생성하므로 인자가 있을 때만 실행한다.

사용:
    uv run python scripts/live_qa.py recipe crm-dashboard      # 결정적 레시피 검증
    uv run python scripts/live_qa.py prompt "운동 습관 트래커 만들어줘"   # 실제 AI 파이프라인 E2E
"""

import asyncio
import json
import sys
from pathlib import Path

from app.agent.creation_executor import CreationExecutor
from app.agent.tools.add_database_items import AddDatabaseItemsTool
from app.notion.client import NotionClient

ROOT = Path(__file__).resolve().parents[2]


async def _inspect_dbs(client: NotionClient, result: dict, expected_samples: dict | None = None) -> list[str]:
    issues: list[str] = []
    pages = result.get("pages", [])
    dbs = result.get("databases", [])
    print(f"페이지: {len(pages)} | DB: {len(dbs)} | 블록: {result.get('blocks', 0)}")
    print(f"URL: {result.get('main_url')}")
    print("\n-- DB별 검증 --")
    for db in dbs:
        db_id = db["id"]
        title = db.get("title", "?")
        ds_id = await client.get_data_source_id(db_id)
        ds = await client.get_data_source(ds_id)
        props = ds.get("properties", {}) or (await client.get_database(db_id)).get("properties", {})
        types = {n: p.get("type") for n, p in props.items()}
        rollup = [n for n, t in types.items() if t == "rollup"]
        formula = [n for n, t in types.items() if t == "formula"]
        relation = [n for n, t in types.items() if t == "relation"]
        rows = await client.query_database(db_id)
        if expected_samples is not None:
            exp = expected_samples.get(title, 0)
            mark = "✅" if len(rows) == exp else "⚠️"
            print(f"  [{title}] 속성 {len(props)} | 샘플행 {len(rows)}/{exp} {mark}")
            if len(rows) != exp:
                issues.append(f"{title}: 샘플행 {len(rows)}/{exp}")
        else:
            mark = "✅" if len(rows) >= 1 else "⚠️"
            print(f"  [{title}] 속성 {len(props)} | 샘플행 {len(rows)} {mark}")
            if len(rows) < 1:
                issues.append(f"{title}: 샘플행 0개 (AI가 샘플 미생성)")
        print(f"      relation={relation} rollup={rollup} formula={formula}")
        if not any(t == "title" for t in types.values()):
            issues.append(f"{title}: title 속성 없음")
    return issues


def _verdict(issues: list[str]) -> int:
    print("\n=== QA 결과 ===")
    if issues:
        print("⚠️ 이슈:")
        for i in issues:
            print("  -", i)
        return 2
    print("✅ 모든 검증 통과")
    return 0


async def qa_recipe(recipe_id: str) -> int:
    fp = ROOT / "recipes" / f"{recipe_id}.json"
    if not fp.exists():
        print(f"레시피 없음: {fp}")
        return 1
    bp = json.loads(fp.read_text(encoding="utf-8"))["blueprint"]
    expected = {db.get("title"): len(db.get("sample_items", [])) for db in bp.get("databases", [])}
    client = NotionClient()
    if client.mock_mode:
        print("mock 모드 — Notion 키 없음. 중단")
        return 1
    print(f"=== 라이브 QA (recipe): {recipe_id} ===")
    executor = CreationExecutor(client, AddDatabaseItemsTool(client))
    result = await executor.execute_blueprint(bp, client.parent_page_id)
    issues = await _inspect_dbs(client, result, expected)
    await client.close()
    return _verdict(issues)


async def qa_prompt(prompt: str) -> int:
    """실제 AI 파이프라인 E2E — 자연어 → 의도분석 → AI 설계 → Notion 생성."""
    from app.agent.orchestrator import AgentOrchestrator

    client = NotionClient()
    if client.mock_mode:
        print("mock 모드 — Notion 키 없음. 중단")
        return 1
    print(f'=== 라이브 QA (AI 파이프라인): "{prompt}" ===')
    agent = AgentOrchestrator()
    agent.require_approval = False  # 비대화형 자동 진행
    result = None
    async for ev in agent.process(prompt):
        t = ev.get("type")
        if t == "progress":
            print(f"  · {ev.get('message', '')[:80]}")
        elif t == "blueprint_preview":
            meta = ev.get("blueprint", {}).get("metadata", {})
            print(f"  [설계] skill={meta.get('skill_used')} layout={meta.get('layout')}")
        elif t == "complete":
            result = ev.get("result")
        elif t == "error":
            print(f"  [에러] {ev.get('content')}")
            return 2
    if not result:
        print("완료 결과 없음")
        return 2
    issues = await _inspect_dbs(client, result, expected_samples=None)
    await client.close()
    return _verdict(issues)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('사용: live_qa.py recipe <id>  |  live_qa.py prompt "<text>"')
        sys.exit(1)
    mode, arg = sys.argv[1], sys.argv[2]
    if mode == "recipe":
        sys.exit(asyncio.run(qa_recipe(arg)))
    elif mode == "prompt":
        sys.exit(asyncio.run(qa_prompt(arg)))
    else:
        print(f"알 수 없는 모드: {mode}")
        sys.exit(1)
