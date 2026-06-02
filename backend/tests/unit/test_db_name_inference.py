"""DB 이름 유추 테스트 (E2E 품질보정) — AI가 title 누락 시 'generic 데이터베이스 N' 방지."""

from app.agent.blueprint_generator import _assemble_blueprint, _infer_db_name


def _content_two_db_no_titles() -> dict:
    """2 DB, 둘 다 title 누락, 서로를 relation으로 가리킴."""
    return {
        "title": "CRM",
        "color": "blue",
        "blocks": [{"type": "callout", "text": "x"}, {"type": "database_ref", "db_index": 0}],
        "databases": [
            {
                "db_properties": {"이름": "title", "거래": {"type": "relation", "target_db_index": 1}},
                "sample_items": [{"이름": "A"}, {"이름": "B"}, {"이름": "C"}],
            },
            {
                "db_properties": {"딜명": "title", "고객": {"type": "relation", "target_db_index": 0}},
                "sample_items": [{"딜명": "d1"}, {"딜명": "d2"}, {"딜명": "d3"}],
            },
        ],
    }


def test_infer_db_name_from_reverse_relation():
    dbs = _content_two_db_no_titles()["databases"]
    assert _infer_db_name(dbs, 0) == "고객"  # DB1의 '고객' relation → DB0
    assert _infer_db_name(dbs, 1) == "거래"  # DB0의 '거래' relation → DB1


def test_infer_returns_none_without_pointing_relation():
    dbs = [{"db_properties": {"이름": "title"}}, {"db_properties": {"제목": "title"}}]
    assert _infer_db_name(dbs, 0) is None


def test_assemble_uses_inferred_names_not_generic():
    bp = _assemble_blueprint(_content_two_db_no_titles(), "CRM")
    titles = [d["title"] for d in bp["databases"]]
    assert not any(t.startswith("데이터베이스") for t in titles), f"generic DB명 발생: {titles}"
    assert "고객" in titles and "거래" in titles


def test_assemble_keeps_explicit_titles():
    content = _content_two_db_no_titles()
    content["databases"][0]["title"] = "VIP 고객"
    bp = _assemble_blueprint(content, "CRM")
    assert bp["databases"][0]["title"] == "VIP 고객"  # 명시 title 보존
