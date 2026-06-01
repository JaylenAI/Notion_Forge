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


async def test_post_process_relations_all_single_property(monkeypatch):
    """양방향 relation 쌍이라도 양측 모두 single_property로 생성 — 선언 이름 보존 (CE-01 회귀).

    dual_property는 반대편 이름을 Notion 자동명으로 바꿔 그 측 rollup을 깨뜨리므로 사용하지 않는다.
    rollup은 자기 측 relation이 채워지면 단방향이어도 정상 집계된다.
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
    assert len(dual) == 0, f"dual_property는 사용하지 않아야 함: {rels}"
    assert len(single) == 2, f"양측 relation 모두 single_property로 생성돼야 함: {rels}"


async def test_sample_links_resolve_index_ref_and_mirror(monkeypatch):
    """AI가 relation 값을 {db_index,item_index} 또는 제목으로 줘도 해석하고, single_property
    역방향을 미러링해 부모(고객)의 rollup이 집계되도록 양쪽을 채운다 (CRM 라이브 회귀)."""
    client = _mock_client(monkeypatch)
    db_rows = {
        "dbA": [{"id": "c0", "properties": {"고객명": {"type": "title", "title": [{"plain_text": "삼성전자"}]}}}],
        "dbB": [
            {"id": "d0", "properties": {"거래명": {"type": "title", "title": [{"plain_text": "딜A"}]}}},
            {"id": "d1", "properties": {"거래명": {"type": "title", "title": [{"plain_text": "딜B"}]}}},
        ],
    }

    async def _q(db_id, **kw):
        return db_rows.get(db_id, [])

    updates: dict = {}

    async def _up(page_id, **kw):
        updates[page_id] = kw["properties"]
        return {"id": page_id}

    monkeypatch.setattr(client, "query_database", _q)
    monkeypatch.setattr(client, "update_page", _up)
    executor = CreationExecutor(client, AddDatabaseItemsTool(client))
    blueprint = {
        "databases": [
            {
                "title": "고객",
                "db_properties": {
                    "고객명": "title",
                    "거래목록": {"type": "relation", "target_db_index": 1},
                    "총거래액": {"type": "rollup", "relation_property": "거래목록", "target_property": "금액", "function": "sum"},
                },
                "sample_items": [{"고객명": "삼성전자"}],
            },
            {
                "title": "거래",
                "db_properties": {"거래명": "title", "고객": {"type": "relation", "target_db_index": 0}},
                "sample_items": [
                    {"거래명": "딜A", "고객": {"db_index": 0, "item_index": 0}},  # 위치 참조
                    {"거래명": "딜B", "고객": "삼성전자"},  # 제목 문자열
                ],
            },
        ]
    }
    result = {"databases": [{"id": "dbA", "title": "고객"}, {"id": "dbB", "title": "거래"}]}
    await executor.post_process_sample_links(blueprint, result)

    # 자식(거래) 양쪽 모두 고객=c0 으로 링크 (index-ref + 제목 둘 다 해석)
    assert updates["d0"]["고객"]["relation"] == [{"id": "c0"}]
    assert updates["d1"]["고객"]["relation"] == [{"id": "c0"}]
    # 미러링: 부모(고객 c0)의 거래목록에 두 딜이 모두 채워져 rollup 총거래액이 집계됨
    linked = {r["id"] for r in updates["c0"]["거래목록"]["relation"]}
    assert linked == {"d0", "d1"}, f"미러링으로 부모 거래목록에 양쪽 자식이 채워져야 함: {linked}"


async def test_format_value_date_accepts_dict_range():
    """AI가 날짜를 dict({start,end})로 줘도 깨지지 않고 ISO 범위로 변환 (OKR 라이브 회귀)."""
    from app.agent.tools.add_database_items import _format_value

    assert _format_value("date", {"start": "2026-01-01", "end": "2026-03-31"}) == {
        "date": {"start": "2026-01-01", "end": "2026-03-31"}
    }
    assert _format_value("date", {"start": "2026-01-01T09:00:00"}) == {"date": {"start": "2026-01-01"}}
    assert _format_value("date", "2026-04-25") == {"date": {"start": "2026-04-25"}}
    assert _format_value("date", "") == {"date": None}


def test_assemble_blueprint_title_fallback_from_user_message():
    """AI(Groq 등)가 title을 안 주거나 'My Template' 기본값을 주면 사용자 요청에서 한국어 제목 생성 (라이브 회귀)."""
    from app.agent.blueprint_generator import _assemble_blueprint

    bp = _assemble_blueprint({"databases": [], "blocks": []}, "회의록 작성 템플릿 만들어줘")
    assert bp["main_page"]["title"] not in ("My Template", "Untitled", "")
    assert "회의록" in bp["main_page"]["title"]

    bp2 = _assemble_blueprint({"title": "My Template"}, "가계부 만들어줘")
    assert bp2["main_page"]["title"] != "My Template"
    assert "가계부" in bp2["main_page"]["title"]

    # 정상 한국어 title은 그대로 보존
    bp3 = _assemble_blueprint({"title": "독서 기록"}, "아무거나")
    assert bp3["main_page"]["title"] == "독서 기록"

    # user_message도 없으면 영어 기본값 대신 한국어 기본값
    bp4 = _assemble_blueprint({}, "")
    assert bp4["main_page"]["title"] == "새 템플릿"


def test_strip_leading_emoji():
    """제목 선두 이모지 제거 — 아이콘과 중복('📚 📚 ...') 방지 (전 템플릿 라이브 회귀)."""
    from app.agent.blueprint_generator import _strip_leading_emoji

    assert _strip_leading_emoji("📚 독서 기록 트래커") == "독서 기록 트래커"
    assert _strip_leading_emoji("🎯 OKR 목표 관리") == "OKR 목표 관리"
    assert _strip_leading_emoji("운동 관리") == "운동 관리"  # 이모지 없으면 그대로
    assert _strip_leading_emoji("📚📚 중복") == "중복"
    assert _strip_leading_emoji("📚") == "📚"  # 전부 이모지면 원본 유지


async def test_post_process_derived_round_retry(monkeypatch):
    """cross-DB rollup-of-formula 등 의존 순서는 라운드 재시도로 해소돼야 한다 (라이브 검증: OKR).

    rollup(진행률)이 다른 DB의 formula(달성률)를 참조 → 1라운드 실패, formula 생성 후 2라운드 성공.
    """
    client = _mock_client(monkeypatch)
    attempts: dict = {}

    async def _spy(db_id, updates):
        name = next(iter(updates["properties"]))
        attempts[name] = attempts.get(name, 0) + 1
        if name == "진행률" and attempts[name] == 1:
            return {"id": db_id, "fallback": True}  # 1라운드: 달성률 미존재로 실패 시뮬
        return {"id": db_id}

    monkeypatch.setattr(client, "update_database", _spy)
    executor = CreationExecutor(client, AddDatabaseItemsTool(client))
    blueprint = {
        "databases": [
            {
                "title": "O",
                "db_properties": {
                    "이름": "title",
                    "관련KR": {"type": "relation", "target_db_index": 1},
                    "진행률": {
                        "type": "rollup",
                        "relation_property": "관련KR",
                        "target_property": "달성률",
                        "function": "average",
                    },
                },
            },
            {
                "title": "KR",
                "db_properties": {
                    "이름": "title",
                    "달성률": {"type": "formula", "expression": "1"},
                    "관련O": {"type": "relation", "target_db_index": 0},
                },
            },
        ]
    }
    result = {"databases": [{"id": "o", "title": "O"}, {"id": "kr", "title": "KR"}]}
    await executor.post_process_relations(blueprint, result)
    assert attempts.get("진행률", 0) >= 2, "진행률 rollup이 재시도되지 않음"


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
