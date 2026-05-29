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
