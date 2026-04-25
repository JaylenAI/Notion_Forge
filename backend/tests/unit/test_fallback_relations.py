"""Fallback 템플릿 Relation/Formula/Rollup/LinkedView 검증 테스트"""

import json
from pathlib import Path

import pytest

from app.agent.blueprint_generator import _evaluate_ai_output, _smart_fallback

TEMPLATES_PATH = Path(__file__).parent.parent.parent / "app" / "agent" / "data" / "fallback_templates.json"


@pytest.fixture
def templates():
    with open(TEMPLATES_PATH) as f:
        return json.load(f)["templates"]


class TestFallbackRelations:
    def test_all_templates_have_valid_json(self, templates):
        assert len(templates) == 8

    @pytest.mark.parametrize(
        "name,expected_dbs",
        [
            ("운동", 2),
            ("독서", 2),
            ("프로젝트", 2),
            ("가계부", 2),
            ("일기", 1),
            ("콘텐츠", 2),
            ("학업", 4),
            ("비즈니스", 4),
        ],
    )
    def test_db_count(self, templates, name, expected_dbs):
        assert len(templates[name]["databases"]) == expected_dbs

    def test_exercise_relation(self, templates):
        db0 = templates["운동"]["databases"][0]["db_properties"]
        assert db0["루틴"]["type"] == "relation"
        assert db0["루틴"]["target_db_index"] == 1

    def test_exercise_formula(self, templates):
        db0 = templates["운동"]["databases"][0]["db_properties"]
        assert db0["효율(cal/min)"]["type"] == "formula"
        assert "칼로리" in db0["효율(cal/min)"]["expression"]

    def test_reading_relation(self, templates):
        db0 = templates["독서"]["databases"][0]["db_properties"]
        assert db0["저자 정보"]["type"] == "relation"
        assert db0["저자 정보"]["target_db_index"] == 1

    def test_reading_formula(self, templates):
        db0 = templates["독서"]["databases"][0]["db_properties"]
        assert db0["평점 등급"]["type"] == "formula"
        assert "평점" in db0["평점 등급"]["expression"]

    def test_project_relation_and_dday(self, templates):
        db0 = templates["프로젝트"]["databases"][0]["db_properties"]
        assert db0["마일스톤"]["type"] == "relation"
        assert db0["마일스톤"]["target_db_index"] == 1
        assert db0["D-Day"]["type"] == "formula"
        assert "dateBetween" in db0["D-Day"]["expression"]

    def test_finance_relation(self, templates):
        db0 = templates["가계부"]["databases"][0]["db_properties"]
        assert db0["예산 항목"]["type"] == "relation"
        assert db0["예산 항목"]["target_db_index"] == 1

    def test_diary_formula(self, templates):
        db0 = templates["일기"]["databases"][0]["db_properties"]
        assert db0["에너지 레벨"]["type"] == "formula"
        assert "에너지" in db0["에너지 레벨"]["expression"]

    def test_content_relation_and_formula(self, templates):
        db0 = templates["콘텐츠"]["databases"][0]["db_properties"]
        assert db0["아이디어"]["type"] == "relation"
        assert db0["아이디어"]["target_db_index"] == 1
        assert db0["발행 D-Day"]["type"] == "formula"

    def test_study_relations_to_subjects(self, templates):
        for di in [1, 2, 3]:
            db = templates["학업"]["databases"][di]["db_properties"]
            assert db["과목"]["type"] == "relation"
            assert db["과목"]["target_db_index"] == 0

    def test_study_dday_formulas(self, templates):
        db1 = templates["학업"]["databases"][1]["db_properties"]
        db2 = templates["학업"]["databases"][2]["db_properties"]
        assert db1["D-Day"]["type"] == "formula"
        assert db2["D-Day"]["type"] == "formula"

    def test_study_rollup(self, templates):
        db1 = templates["학업"]["databases"][1]["db_properties"]
        assert db1["학점"]["type"] == "rollup"
        assert db1["학점"]["relation_property"] == "과목"
        assert db1["학점"]["target_property"] == "학점"
        assert db1["학점"]["function"] == "sum"

    def test_business_relations(self, templates):
        dbs = templates["비즈니스"]["databases"]
        assert dbs[0]["db_properties"]["고객"]["type"] == "relation"
        assert dbs[0]["db_properties"]["고객"]["target_db_index"] == 1
        assert dbs[2]["db_properties"]["프로젝트"]["type"] == "relation"
        assert dbs[2]["db_properties"]["프로젝트"]["target_db_index"] == 0
        assert dbs[3]["db_properties"]["관련 고객"]["type"] == "relation"
        assert dbs[3]["db_properties"]["관련 고객"]["target_db_index"] == 1

    def test_business_dday(self, templates):
        db0 = templates["비즈니스"]["databases"][0]["db_properties"]
        assert db0["D-Day"]["type"] == "formula"


class TestLinkedViews:
    @pytest.mark.parametrize(
        "name",
        ["운동", "독서", "프로젝트", "가계부", "일기", "콘텐츠", "학업", "비즈니스"],
    )
    def test_has_linked_view(self, templates, name):
        blocks = templates[name]["blocks"]
        linked_views = [b for b in blocks if b.get("type") == "linked_view"]
        assert len(linked_views) >= 1, f"{name}: linked_view 블록이 없습니다"

    def test_linked_view_db_index_valid(self, templates):
        for name, t in templates.items():
            db_count = len(t["databases"])
            for block in t["blocks"]:
                if block.get("type") == "linked_view":
                    assert block["db_index"] < db_count, f"{name}: db_index {block['db_index']} >= {db_count}"


class TestRelationTargetIndexValid:
    def test_all_relation_targets_in_range(self, templates):
        for name, t in templates.items():
            db_count = len(t["databases"])
            for di, db in enumerate(t["databases"]):
                props = db.get("db_properties", {})
                for pname, pspec in props.items():
                    if isinstance(pspec, dict) and pspec.get("type") == "relation":
                        idx = pspec["target_db_index"]
                        assert 0 <= idx < db_count, f"{name}.DB{di}.{pname}: target_db_index={idx} 범위 초과"
                        assert idx != di, f"{name}.DB{di}.{pname}: 자기 참조 relation"

    def test_rollup_relation_exists(self, templates):
        for name, t in templates.items():
            for di, db in enumerate(t["databases"]):
                props = db.get("db_properties", {})
                for pname, pspec in props.items():
                    if isinstance(pspec, dict) and pspec.get("type") == "rollup":
                        rel_prop = pspec["relation_property"]
                        assert rel_prop in props, (
                            f"{name}.DB{di}.{pname}: rollup의 relation_property '{rel_prop}' 미존재"
                        )
                        assert isinstance(props[rel_prop], dict), f"{name}.DB{di}: '{rel_prop}'가 dict가 아님"
                        assert props[rel_prop].get("type") == "relation", (
                            f"{name}.DB{di}: '{rel_prop}'가 relation 타입이 아님"
                        )


class TestGenEvalLevel5:
    def test_valid_relation_passes(self):
        content = {
            "blocks": [
                {"type": "callout", "text": "Hi", "icon": "🔥"},
                {"type": "heading_1", "text": "DB"},
                {"type": "database_ref", "db_index": 0},
                {"type": "database_ref", "db_index": 1},
            ],
            "databases": [
                {
                    "title": "A",
                    "db_properties": {"이름": "title", "링크": {"type": "relation", "target_db_index": 1}},
                    "sample_items": [{}, {}, {}],
                },
                {"title": "B", "db_properties": {"이름": "title"}, "sample_items": [{}, {}, {}]},
            ],
        }
        is_pass, errors = _evaluate_ai_output(content)
        relation_errors = [e for e in errors if "relation" in e.lower() or "target_db_index" in e]
        assert len(relation_errors) == 0

    def test_invalid_relation_target(self):
        content = {
            "blocks": [
                {"type": "callout", "text": "Hi", "icon": "🔥"},
                {"type": "heading_1", "text": "DB"},
                {"type": "database_ref", "db_index": 0},
            ],
            "databases": [
                {
                    "title": "A",
                    "db_properties": {"이름": "title", "링크": {"type": "relation", "target_db_index": 5}},
                    "sample_items": [{}, {}, {}],
                },
            ],
        }
        is_pass, errors = _evaluate_ai_output(content)
        assert any("target_db_index" in e for e in errors)

    def test_self_referencing_relation(self):
        content = {
            "blocks": [
                {"type": "callout", "text": "Hi", "icon": "🔥"},
                {"type": "heading_1", "text": "DB"},
                {"type": "database_ref", "db_index": 0},
            ],
            "databases": [
                {
                    "title": "A",
                    "db_properties": {"이름": "title", "링크": {"type": "relation", "target_db_index": 0}},
                    "sample_items": [{}, {}, {}],
                },
            ],
        }
        is_pass, errors = _evaluate_ai_output(content)
        assert any("자기 자신" in e for e in errors)

    def test_formula_without_expression(self):
        content = {
            "blocks": [
                {"type": "callout", "text": "Hi", "icon": "🔥"},
                {"type": "heading_1", "text": "DB"},
                {"type": "database_ref", "db_index": 0},
            ],
            "databases": [
                {
                    "title": "A",
                    "db_properties": {"이름": "title", "수식": {"type": "formula"}},
                    "sample_items": [{}, {}, {}],
                },
            ],
        }
        is_pass, errors = _evaluate_ai_output(content)
        assert any("expression" in e for e in errors)

    def test_rollup_without_relation_property(self):
        content = {
            "blocks": [
                {"type": "callout", "text": "Hi", "icon": "🔥"},
                {"type": "heading_1", "text": "DB"},
                {"type": "database_ref", "db_index": 0},
            ],
            "databases": [
                {
                    "title": "A",
                    "db_properties": {"이름": "title", "집계": {"type": "rollup"}},
                    "sample_items": [{}, {}, {}],
                },
            ],
        }
        is_pass, errors = _evaluate_ai_output(content)
        assert any("relation_property" in e for e in errors)

    def test_rollup_references_nonexistent_relation(self):
        content = {
            "blocks": [
                {"type": "callout", "text": "Hi", "icon": "🔥"},
                {"type": "heading_1", "text": "DB"},
                {"type": "database_ref", "db_index": 0},
            ],
            "databases": [
                {
                    "title": "A",
                    "db_properties": {
                        "이름": "title",
                        "집계": {
                            "type": "rollup",
                            "relation_property": "없는속성",
                            "target_property": "이름",
                            "function": "count",
                        },
                    },
                    "sample_items": [{}, {}, {}],
                },
            ],
        }
        is_pass, errors = _evaluate_ai_output(content)
        assert any("존재하지 않습니다" in e for e in errors)


class TestSmartFallbackWithRelations:
    def test_fallback_passes_gen_eval(self):
        for keyword in ["운동", "독서", "프로젝트", "가계부", "일기", "콘텐츠", "학업", "비즈니스"]:
            result = _smart_fallback(f"{keyword} 만들어줘")
            is_pass, errors = _evaluate_ai_output(result)
            assert is_pass, f"{keyword} 폴백 Gen-Eval 실패: {errors}"
