"""sub_page 키 호환성 회귀 테스트 — 라이브 E2E에서 발견한 버그 고정.

recipe/golden 은 sub_pages에 'name' 키를, AI/스키마는 'title' 키를 쓴다.
creation_executor가 'title'만 접근하면 KeyError로 생성이 크래시했다(핸들러도 2차 크래시).
"""

from app.agent.creation_executor import CreationExecutor
from app.agent.tools.add_database_items import AddDatabaseItemsTool
from app.notion.client import NotionClient


def _mock_client(monkeypatch) -> NotionClient:
    from app.config import settings

    monkeypatch.setattr(settings, "notion_api_key", "", raising=False)
    monkeypatch.setattr(settings, "notion_parent_page_id", "", raising=False)
    client = NotionClient()
    assert client.mock_mode, "테스트는 mock 모드여야 한다 (실제 Notion 호출 금지)"
    return client


async def test_execute_blueprint_handles_subpage_name_key(monkeypatch):
    client = _mock_client(monkeypatch)
    executor = CreationExecutor(client, AddDatabaseItemsTool(client))
    bp = {
        "main_page": {"title": "테스트", "icon": "🧪"},
        "blocks": [{"type": "callout", "text": "hi", "icon": "👋", "color": "blue_background"}],
        "databases": [],
        "sub_pages": [
            {"name": "name키 서브페이지", "icon": "📁", "blocks": [{"type": "paragraph", "text": "x"}]},
        ],
    }
    result = await executor.execute_blueprint(bp, "mock-parent")
    titles = [p.get("title") for p in result.get("pages", [])]
    assert "name키 서브페이지" in titles


async def test_execute_blueprint_handles_subpage_title_key(monkeypatch):
    client = _mock_client(monkeypatch)
    executor = CreationExecutor(client, AddDatabaseItemsTool(client))
    bp = {
        "main_page": {"title": "테스트", "icon": "🧪"},
        "blocks": [],
        "databases": [],
        "sub_pages": [{"title": "title키 서브페이지", "icon": "📄"}],
    }
    result = await executor.execute_blueprint(bp, "mock-parent")
    titles = [p.get("title") for p in result.get("pages", [])]
    assert "title키 서브페이지" in titles


async def test_execute_blueprint_subpage_missing_both_keys_no_crash(monkeypatch):
    """title/name 둘 다 없어도 크래시하지 않고 기본 제목으로 생성."""
    client = _mock_client(monkeypatch)
    executor = CreationExecutor(client, AddDatabaseItemsTool(client))
    bp = {
        "main_page": {"title": "테스트", "icon": "🧪"},
        "blocks": [],
        "databases": [],
        "sub_pages": [{"icon": "❓"}],
    }
    result = await executor.execute_blueprint(bp, "mock-parent")
    # 크래시 없이 완료되면 성공 (메인 페이지는 반드시 존재)
    assert len(result.get("pages", [])) >= 1


async def test_subpage_name_key_blocks_are_filled(monkeypatch):
    """name키 서브페이지의 blocks가 실제 add_blocks로 채워져야 한다 (CE-01 회귀).

    과거 fill_sub_pages가 sub['title']만 접근해 name-only 서브페이지의 블록이 조용히 누락됐다.
    """
    client = _mock_client(monkeypatch)
    added: list = []

    async def _spy_add_blocks(page_id, blocks):
        added.append((page_id, blocks))
        return {"results": []}

    monkeypatch.setattr(client, "add_blocks", _spy_add_blocks)
    executor = CreationExecutor(client, AddDatabaseItemsTool(client))
    bp = {
        "main_page": {"title": "테스트", "icon": "🧪"},
        "blocks": [],
        "databases": [],
        "sub_pages": [
            {"name": "name서브", "icon": "📁", "blocks": [{"type": "paragraph", "text": "채워질 내용"}]},
        ],
    }
    await executor.execute_blueprint(bp, "mock-parent")
    # 메인 blocks=[] 이므로 add_blocks 호출은 서브페이지 충전뿐이어야 함
    assert any(blocks for _, blocks in added), "name키 서브페이지의 블록이 채워지지 않음 (CE-01)"


async def test_post_process_sample_links_sets_relation(monkeypatch):
    """샘플 아이템의 relation 값(대상 제목)이 실제 relation으로 설정돼야 한다 (rollup 실집계).

    라이브 검증: CRM 고객→딜 링크 후 rollup 총딜금액이 실제 합산됨.
    """
    client = _mock_client(monkeypatch)
    db_rows = {
        "dbA": [{"id": "a1", "properties": {"이름": {"type": "title", "title": [{"plain_text": "고객1"}]}}}],
        "dbB": [{"id": "b1", "properties": {"이름": {"type": "title", "title": [{"plain_text": "딜1"}]}}}],
    }

    async def _q(db_id, **kw):
        return db_rows.get(db_id, [])

    updates: list = []

    async def _up(page_id, **kw):
        updates.append((page_id, kw))
        return {"id": page_id}

    monkeypatch.setattr(client, "query_database", _q)
    monkeypatch.setattr(client, "update_page", _up)
    executor = CreationExecutor(client, AddDatabaseItemsTool(client))
    blueprint = {
        "databases": [
            {
                "title": "A",
                "db_properties": {"이름": "title", "링크": {"type": "relation", "target_db_index": 1}},
                "sample_items": [{"이름": "고객1", "링크": ["딜1"]}],
            },
            {"title": "B", "db_properties": {"이름": "title"}, "sample_items": [{"이름": "딜1"}]},
        ]
    }
    result = {"databases": [{"id": "dbA", "title": "A"}, {"id": "dbB", "title": "B"}]}
    await executor.post_process_sample_links(blueprint, result)
    assert updates, "샘플 링크가 설정되지 않음"
    pid, kw = updates[0]
    assert pid == "a1"
    assert kw["properties"]["링크"]["relation"] == [{"id": "b1"}]


async def test_post_process_bidirectional_pair_uses_dual_property(monkeypatch):
    """양방향 relation 쌍은 dual_property 1개로 생성, 반대쪽은 skip (DATA-1, 라이브 검증).

    single_property 두 개면 rollup 자동집계가 안 됨 → dual로 통합해야 양쪽 동기화.
    """
    client = _mock_client(monkeypatch)
    calls: list = []

    async def _spy(db_id, updates):
        calls.append((db_id, updates))
        return {"id": db_id}

    monkeypatch.setattr(client, "update_database", _spy)
    executor = CreationExecutor(client, AddDatabaseItemsTool(client))
    blueprint = {
        "databases": [
            {"title": "A", "db_properties": {"이름": "title", "b링크": {"type": "relation", "target_db_index": 1}}},
            {"title": "B", "db_properties": {"이름": "title", "a링크": {"type": "relation", "target_db_index": 0}}},
        ]
    }
    result = {"databases": [{"id": "dbA", "title": "A"}, {"id": "dbB", "title": "B"}]}
    await executor.post_process_relations(blueprint, result)
    rels = []
    for _db_id, upd in calls:
        for _name, spec in upd.get("properties", {}).items():
            if "relation" in spec:
                rels.append(spec["relation"])
    dual = [r for r in rels if r.get("type") == "dual_property" or "dual_property" in r]
    single = [r for r in rels if "single_property" in r]
    assert len(dual) == 1, f"양방향 쌍은 dual 1개여야 함: {rels}"
    assert len(single) == 0, f"쌍의 반대쪽은 skip되어야 함: {rels}"


async def test_post_process_creates_formula_for_single_db(monkeypatch):
    """단일 DB 템플릿의 formula도 후처리에서 생성돼야 한다 (라이브 E2E 회귀).

    과거 post_process_relations가 DB<2면 조기 반환해 단일 DB formula가 누락됐다.
    """
    client = _mock_client(monkeypatch)
    calls: list[dict] = []

    async def _spy_update(db_id, updates):
        calls.append(updates)
        return {"id": db_id}

    monkeypatch.setattr(client, "update_database", _spy_update)
    executor = CreationExecutor(client, AddDatabaseItemsTool(client))
    blueprint = {
        "databases": [
            {
                "title": "태스크",
                "db_properties": {
                    "이름": "title",
                    "D-Day": {"type": "formula", "expression": "dateBetween(prop(\"기한\"), now(), \"days\")"},
                },
            }
        ]
    }
    result = {"databases": [{"id": "db1", "title": "태스크"}]}
    await executor.post_process_relations(blueprint, result)
    patched_props = {k for u in calls for k in u.get("properties", {})}
    assert "D-Day" in patched_props, "단일 DB formula가 후처리에서 생성되지 않음"
