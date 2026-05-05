"""PostProcessor _validate_view_properties 회귀 테스트

회귀 버그: db["views"]가 문자열 리스트인 경우 (예: ["table", "board"])
isinstance(view, str) 체크 없이 view.get() 호출하여 AttributeError 발생.

수정 후: 문자열 뷰는 건너뛰고 dict 뷰만 검증.
"""

import pytest

from app.agent.post_processor import BlueprintValidator


@pytest.fixture
def validator():
    return BlueprintValidator()


# ============================================================
# _validate_view_properties 회귀 테스트
# ============================================================


class TestValidateViewPropertiesRegression:
    """views 배열에 문자열이 포함된 경우 크래시 방지 확인"""

    def test_views_as_string_list_should_not_crash(self, validator):
        """views = ["table", "board"] (문자열 리스트) -> 크래시 없이 통과"""
        content = {
            "databases": [
                {
                    "title": "Tasks",
                    "db_properties": {
                        "Name": "title",
                        "Status": "status",
                        "Due Date": "date",
                    },
                    "views": ["table", "board"],
                    "sample_items": [],
                }
            ],
            "blocks": [],
        }
        # Should not raise any exception
        result = validator._validate_view_properties(content)
        # Views should remain unchanged
        assert result["databases"][0]["views"] == ["table", "board"]

    def test_views_as_dict_list_normal_validation(self, validator):
        """views = [{"type": "board", "group_by": "Status"}] -> 정상 검증"""
        content = {
            "databases": [
                {
                    "title": "Tasks",
                    "db_properties": {
                        "Name": "title",
                        "Status": "status",
                        "Priority": {"type": "select", "options": ["High", "Low"]},
                    },
                    "views": [{"type": "board", "group_by": "Status"}],
                    "sample_items": [],
                }
            ],
            "blocks": [],
        }
        result = validator._validate_view_properties(content)
        view = result["databases"][0]["views"][0]
        assert view["group_by"] == "Status"

    def test_views_mixed_strings_and_dicts(self, validator):
        """views = ["table", {"type": "calendar", "date_property": "Date"}] -> 혼합"""
        content = {
            "databases": [
                {
                    "title": "Events",
                    "db_properties": {
                        "Name": "title",
                        "Date": "date",
                        "Status": "status",
                    },
                    "views": ["table", {"type": "calendar", "date_property": "Date"}],
                    "sample_items": [],
                }
            ],
            "blocks": [],
        }
        result = validator._validate_view_properties(content)
        views = result["databases"][0]["views"]
        # String view is preserved as-is
        assert views[0] == "table"
        # Dict view is validated
        assert views[1]["type"] == "calendar"
        assert views[1]["date_property"] == "Date"

    def test_board_view_invalid_group_by_autocorrects(self, validator):
        """board 뷰의 group_by가 존재하지 않는 속성일 때 자동 보정"""
        content = {
            "databases": [
                {
                    "title": "Projects",
                    "db_properties": {
                        "Name": "title",
                        "Status": "status",
                        "Category": {"type": "select"},
                    },
                    "views": [{"type": "board", "group_by": "NonexistentProp"}],
                    "sample_items": [],
                }
            ],
            "blocks": [],
        }
        result = validator._validate_view_properties(content)
        view = result["databases"][0]["views"][0]
        # Should fallback to status property
        assert view["group_by"] == "Status"

    def test_board_view_no_group_by_gets_status(self, validator):
        """board 뷰에 group_by가 없으면 status 속성 자동 할당"""
        content = {
            "databases": [
                {
                    "title": "Tasks",
                    "db_properties": {
                        "Name": "title",
                        "Status": "status",
                    },
                    "views": [{"type": "board"}],
                    "sample_items": [],
                }
            ],
            "blocks": [],
        }
        result = validator._validate_view_properties(content)
        view = result["databases"][0]["views"][0]
        assert view["group_by"] == "Status"

    def test_calendar_view_invalid_date_property_autocorrects(self, validator):
        """calendar 뷰의 date_property가 잘못된 경우 자동 보정"""
        content = {
            "databases": [
                {
                    "title": "Schedule",
                    "db_properties": {
                        "Name": "title",
                        "Due Date": "date",
                    },
                    "views": [{"type": "calendar", "date_property": "WrongDate"}],
                    "sample_items": [],
                }
            ],
            "blocks": [],
        }
        result = validator._validate_view_properties(content)
        view = result["databases"][0]["views"][0]
        assert view["date_property"] == "Due Date"

    def test_calendar_view_no_date_property_gets_first_date(self, validator):
        """calendar 뷰에 date_property가 없으면 첫 번째 date 속성 할당"""
        content = {
            "databases": [
                {
                    "title": "Events",
                    "db_properties": {
                        "Name": "title",
                        "Event Date": "date",
                        "End Date": "date",
                    },
                    "views": [{"type": "calendar"}],
                    "sample_items": [],
                }
            ],
            "blocks": [],
        }
        result = validator._validate_view_properties(content)
        view = result["databases"][0]["views"][0]
        assert view["date_property"] == "Event Date"

    def test_timeline_view_invalid_date_property(self, validator):
        """timeline 뷰의 date_property 자동 보정"""
        content = {
            "databases": [
                {
                    "title": "Roadmap",
                    "db_properties": {
                        "Name": "title",
                        "Start": "date",
                    },
                    "views": [{"type": "timeline", "date_property": "BadProp"}],
                    "sample_items": [],
                }
            ],
            "blocks": [],
        }
        result = validator._validate_view_properties(content)
        view = result["databases"][0]["views"][0]
        assert view["date_property"] == "Start"

    def test_chart_view_invalid_x_axis(self, validator):
        """chart 뷰의 x_axis 속성이 잘못된 경우 자동 보정"""
        content = {
            "databases": [
                {
                    "title": "Analytics",
                    "db_properties": {
                        "Name": "title",
                        "Category": {"type": "select"},
                        "Status": "status",
                    },
                    "views": [{"type": "chart", "x_axis": "NonexistentAxis"}],
                    "sample_items": [],
                }
            ],
            "blocks": [],
        }
        result = validator._validate_view_properties(content)
        view = result["databases"][0]["views"][0]
        # Should fallback to first select/status prop
        assert view["x_axis"] in ("Category", "Status")

    def test_empty_views_list(self, validator):
        """빈 views 리스트 처리"""
        content = {
            "databases": [
                {
                    "title": "DB",
                    "db_properties": {"Name": "title"},
                    "views": [],
                    "sample_items": [],
                }
            ],
            "blocks": [],
        }
        result = validator._validate_view_properties(content)
        assert result["databases"][0]["views"] == []

    def test_no_views_key(self, validator):
        """views 키가 없는 경우"""
        content = {
            "databases": [
                {
                    "title": "DB",
                    "db_properties": {"Name": "title"},
                    "sample_items": [],
                }
            ],
            "blocks": [],
        }
        result = validator._validate_view_properties(content)
        assert "views" not in result["databases"][0]

    def test_no_databases(self, validator):
        """databases가 없는 경우"""
        content = {"blocks": []}
        result = validator._validate_view_properties(content)
        assert "databases" not in result

    def test_view_with_view_type_key(self, validator):
        """view_type 키 사용 (type 대신)"""
        content = {
            "databases": [
                {
                    "title": "Tasks",
                    "db_properties": {
                        "Name": "title",
                        "Status": "status",
                    },
                    "views": [{"view_type": "board"}],
                    "sample_items": [],
                }
            ],
            "blocks": [],
        }
        result = validator._validate_view_properties(content)
        view = result["databases"][0]["views"][0]
        assert view.get("group_by") == "Status"

    def test_multiple_databases_with_mixed_views(self, validator):
        """여러 DB에 각각 다른 형태의 views"""
        content = {
            "databases": [
                {
                    "title": "DB1",
                    "db_properties": {"Name": "title", "Status": "status"},
                    "views": ["table"],
                    "sample_items": [],
                },
                {
                    "title": "DB2",
                    "db_properties": {"Name": "title", "Date": "date"},
                    "views": [{"type": "calendar", "date_property": "Date"}],
                    "sample_items": [],
                },
                {
                    "title": "DB3",
                    "db_properties": {"Name": "title"},
                    "views": ["board", {"type": "list"}],
                    "sample_items": [],
                },
            ],
            "blocks": [],
        }
        # Should not crash on any DB
        result = validator._validate_view_properties(content)
        assert len(result["databases"]) == 3

    def test_properties_key_fallback(self, validator):
        """db_properties 없이 properties 키만 있는 경우"""
        content = {
            "databases": [
                {
                    "title": "Tasks",
                    "properties": {
                        "Name": "title",
                        "Status": "status",
                    },
                    "views": [{"type": "board", "group_by": "Status"}],
                    "sample_items": [],
                }
            ],
            "blocks": [],
        }
        result = validator._validate_view_properties(content)
        view = result["databases"][0]["views"][0]
        assert view["group_by"] == "Status"


# ============================================================
# 전체 validate_and_fix 파이프라인 통합 테스트
# ============================================================


class TestValidateAndFixIntegration:
    """validate_and_fix 전체 파이프라인이 views 문자열 리스트에서 크래시하지 않는지 확인"""

    def test_full_pipeline_with_string_views(self, validator):
        """전체 파이프라인에서 문자열 뷰 포함 content 처리"""
        content = {
            "title": "My Template",
            "icon": "📋",
            "color": "blue",
            "databases": [
                {
                    "title": "Tasks",
                    "db_properties": {
                        "Name": "title",
                        "Status": "status",
                        "Priority": {"type": "select", "options": ["High", "Medium", "Low"]},
                        "Due Date": "date",
                    },
                    "views": ["table", "board"],
                    "sample_items": [
                        {"Name": "Task 1", "Status": "진행 중", "Priority": "High"},
                        {"Name": "Task 2", "Status": "완료", "Priority": "Low"},
                        {"Name": "Task 3", "Status": "시작 전", "Priority": "Medium"},
                    ],
                }
            ],
            "blocks": [
                {"type": "heading_1", "text": "Dashboard"},
                {"type": "paragraph", "text": "Welcome"},
                {"type": "database_ref", "db_index": 0},
            ],
            "sub_pages": [],
        }
        # Should complete without error
        result = validator.validate_and_fix(content)
        assert "databases" in result
        assert "blocks" in result
        # Views should still be present
        assert result["databases"][0]["views"] == ["table", "board"]
