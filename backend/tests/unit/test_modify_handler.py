"""ModifyHandler 테스트: 수정 유형 분류 + 디스패치 테이블 검증"""

from unittest.mock import patch

from app.agent.modify_handler import ModifyHandler
from app.notion.client import NotionClient


def _make_mock_handler():
    with patch("app.notion.client.settings") as mock_settings:
        mock_settings.notion_api_key = ""
        mock_settings.notion_parent_page_id = ""
        client = NotionClient(token="", parent_page_id="")
    return ModifyHandler(client=client)


def _result_with_dbs():
    return {"pages": [{"id": "p1"}], "databases": [{"id": "db1"}]}


def _result_without_dbs():
    return {"pages": [{"id": "p1"}], "databases": []}


class TestClassifyModifyType:
    def test_delete_property(self):
        result = ModifyHandler._classify_modify_type("속성 삭제해줘", _result_with_dbs())
        assert result == "delete_property"

    def test_add_property(self):
        result = ModifyHandler._classify_modify_type("태그 속성 추가해줘", _result_with_dbs())
        assert result == "add_property"

    def test_add_view_board(self):
        result = ModifyHandler._classify_modify_type("보드 뷰 추가해줘", _result_with_dbs())
        assert result == "add_view"

    def test_add_view_calendar(self):
        result = ModifyHandler._classify_modify_type("캘린더 뷰로 보여줘", _result_with_dbs())
        assert result == "add_view"

    def test_add_view_gallery(self):
        result = ModifyHandler._classify_modify_type("갤러리 뷰 넣어줘", _result_with_dbs())
        assert result == "add_view"

    def test_delete_view(self):
        result = ModifyHandler._classify_modify_type("보드 뷰 삭제해줘", _result_with_dbs())
        assert result == "delete_item"

    def test_add_formula(self):
        result = ModifyHandler._classify_modify_type("D-Day 수식 추가해줘", _result_with_dbs())
        assert result == "add_formula"

    def test_add_relation(self):
        result = ModifyHandler._classify_modify_type("DB 연결해줘", _result_with_dbs())
        assert result == "add_relation"

    def test_add_database(self):
        result = ModifyHandler._classify_modify_type("새 데이터베이스 추가해줘", _result_with_dbs())
        assert result == "add_database"

    def test_add_sub_page(self):
        result = ModifyHandler._classify_modify_type("하위 페이지 추가해줘", _result_with_dbs())
        assert result == "add_sub_page"

    def test_add_block(self):
        result = ModifyHandler._classify_modify_type("FAQ 블록 추가해줘", _result_with_dbs())
        assert result == "add_block"

    def test_delete_block(self):
        result = ModifyHandler._classify_modify_type("블록 삭제해줘", _result_with_dbs())
        assert result == "delete_item"

    def test_modify_default(self):
        result = ModifyHandler._classify_modify_type("좀 바꿔줘", _result_with_dbs())
        assert result == "modify_default"

    def test_no_dbs_skips_db_specific(self):
        result = ModifyHandler._classify_modify_type("속성 삭제해줘", _result_without_dbs())
        assert result == "modify_default"


class TestHandlerDispatchTable:
    def test_all_handlers_exist(self):
        handler = _make_mock_handler()
        for modify_type, method_name in ModifyHandler._HANDLERS.items():
            assert hasattr(handler, method_name), f"{method_name} not found"


class TestHandleModifyNoTemplate:
    async def test_no_result_yields_message(self):
        handler = _make_mock_handler()
        events = []
        async for event in handler.handle_modify("수정해줘", None, None, None):
            events.append(event)
        assert any("없습니다" in e.get("content", "") for e in events)

    async def test_empty_pages_yields_message(self):
        handler = _make_mock_handler()
        events = []
        async for event in handler.handle_modify("수정해줘", None, {"pages": []}, None):
            events.append(event)
        assert any("없습니다" in e.get("content", "") for e in events)
