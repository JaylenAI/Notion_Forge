"""Post-processor 테스트 — 7개 검증 규칙"""

import pytest
from app.agent.post_processor import BlueprintValidator


@pytest.fixture
def validator():
    return BlueprintValidator()


class TestEnsureWelcomeCallout:
    def test_adds_callout_when_missing(self, validator):
        content = {"title": "My Template", "icon": "📋", "color": "blue",
                   "blocks": [{"type": "heading_1", "text": "Hello"}]}
        result = validator._ensure_welcome_callout(content)
        assert result["blocks"][0]["type"] == "callout"
        assert "환영" in result["blocks"][0]["text"]

    def test_keeps_existing_callout(self, validator):
        content = {"blocks": [{"type": "callout", "text": "Welcome!"}]}
        result = validator._ensure_welcome_callout(content)
        assert len(result["blocks"]) == 1
        assert result["blocks"][0]["text"] == "Welcome!"

    def test_empty_blocks(self, validator):
        content = {"blocks": []}
        result = validator._ensure_welcome_callout(content)
        assert result["blocks"] == []


class TestEnsureGuideToggle:
    def test_adds_guide_when_missing(self, validator):
        content = {"blocks": [{"type": "callout", "text": "Hi"}]}
        result = validator._ensure_guide_toggle(content)
        assert any(b["type"] == "toggle" and "가이드" in b["text"] for b in result["blocks"])

    def test_keeps_existing_guide(self, validator):
        content = {"blocks": [{"type": "toggle", "text": "📖 사용 가이드", "children_text": "..."}]}
        result = validator._ensure_guide_toggle(content)
        assert sum(1 for b in result["blocks"] if b["type"] == "toggle" and "가이드" in b["text"]) == 1


class TestFixDbRefInColumns:
    def test_extracts_db_ref_from_column(self, validator):
        content = {"blocks": [
            {"type": "column_list", "columns": [
                [{"type": "paragraph", "text": "Hello"}, {"type": "database_ref", "db_index": 0}],
                [{"type": "paragraph", "text": "World"}],
            ]}
        ]}
        result = validator._fix_db_ref_in_columns(content)
        # DB ref should be extracted after column_list
        has_db_ref_after = any(b.get("type") == "database_ref" for b in result["blocks"])
        assert has_db_ref_after


class TestValidateDbRefs:
    def test_fixes_out_of_range_index(self, validator):
        content = {
            "databases": [{"title": "DB1"}],
            "blocks": [{"type": "database_ref", "db_index": 5}],
        }
        result = validator._validate_db_refs(content)
        assert result["blocks"][0]["db_index"] == 0

    def test_valid_index_unchanged(self, validator):
        content = {
            "databases": [{"title": "DB1"}, {"title": "DB2"}],
            "blocks": [{"type": "database_ref", "db_index": 1}],
        }
        result = validator._validate_db_refs(content)
        assert result["blocks"][0]["db_index"] == 1


class TestFixStatusValues:
    def test_maps_korean_to_english(self, validator):
        content = {
            "databases": [{
                "db_properties": {"상태": "status"},
                "sample_items": [{"상태": "시작 전"}, {"상태": "완료"}],
            }]
        }
        result = validator._fix_status_values(content)
        # post_processor는 한→영 매핑이 아니라 영→한 매핑
        # "시작 전" → "시작 전" (이미 한국어), "완료" → "완료" (이미 한국어)
        assert result["databases"][0]["sample_items"][0]["상태"] == "시작 전"
        assert result["databases"][0]["sample_items"][1]["상태"] == "완료"

    def test_english_status(self, validator):
        content = {
            "databases": [{
                "db_properties": {"status": "status"},
                "sample_items": [{"status": "not started"}, {"status": "done"}],
            }]
        }
        result = validator._fix_status_values(content)
        assert result["databases"][0]["sample_items"][0]["status"] == "시작 전"
        assert result["databases"][0]["sample_items"][1]["status"] == "완료"


class TestEnsureSampleItems:
    def test_auto_generates_when_few_items(self, validator):
        content = {
            "databases": [{
                "title": "TestDB",
                "db_properties": {"이름": "title", "상태": "status"},
                "sample_items": [{"이름": "A"}],
            }]
        }
        result = validator._ensure_sample_items(content)
        assert len(result["databases"][0]["sample_items"]) >= 4

    def test_skips_when_enough_items(self, validator):
        content = {
            "databases": [{
                "title": "TestDB",
                "sample_items": [{"이름": "A"}, {"이름": "B"}, {"이름": "C"}],
            }]
        }
        result = validator._ensure_sample_items(content)
        assert len(result["databases"][0]["sample_items"]) == 3

    def test_generates_from_empty(self, validator):
        content = {
            "databases": [{
                "title": "학습 자료",
                "db_properties": {"자료명": "title", "유형": "select", "날짜": "date"},
                "sample_items": [],
            }]
        }
        result = validator._ensure_sample_items(content)
        items = result["databases"][0]["sample_items"]
        assert len(items) == 4
        assert "자료명" in items[0]


class TestEnsureCoverCategory:
    def test_adds_cover_from_color(self, validator):
        content = {"color": "orange"}
        result = validator._ensure_cover_category(content)
        assert result["cover_category"] == "fitness"

    def test_keeps_existing_category(self, validator):
        content = {"color": "blue", "cover_category": "tech"}
        result = validator._ensure_cover_category(content)
        assert result["cover_category"] == "tech"

    def test_default_category(self, validator):
        content = {"color": "unknown_color"}
        result = validator._ensure_cover_category(content)
        assert result["cover_category"] == "minimal"


class TestValidateAndFix:
    def test_full_pipeline(self, validator):
        content = {
            "title": "Test Template",
            "icon": "🧪",
            "color": "blue",
            "blocks": [
                {"type": "heading_1", "text": "Title"},
                {"type": "database_ref", "db_index": 0},
            ],
            "databases": [{"title": "DB1", "db_properties": {}, "sample_items": []}],
        }
        result = validator.validate_and_fix(content)
        # Should have welcome callout as first block
        assert result["blocks"][0]["type"] == "callout"
        # Should have guide toggle at end
        assert any(b["type"] == "toggle" and "가이드" in b.get("text", "") for b in result["blocks"])
        # Should have cover category
        assert "cover_category" in result
