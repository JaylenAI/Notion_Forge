"""Phase 2 기능 확장 테스트: filter_builder, widget_builder, numbered_list 확장,
view_ops 신규 메서드, page/database template 지원"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.notion.block_builder import numbered_list
from app.notion.filter_builder import (
    compound_filter,
    date_filter,
    multi_select_filter,
    people_filter,
    select_filter,
    status_filter,
)
from app.notion.widget_builder import (
    chart_widget,
    filtered_view_widget,
    list_widget,
    number_widget,
    widget_position,
)

# ============================================================
# filter_builder 테스트
# ============================================================


class TestDateFilter:
    def test_relative_date_today(self):
        result = date_filter("Due Date", "on_or_after", "today")
        assert result["property"] == "Due Date"
        assert result["date"]["on_or_after"]["relative_date"] == "today"

    def test_relative_date_one_week_ago(self):
        result = date_filter("Created", "after", "one_week_ago")
        assert result["date"]["after"]["relative_date"] == "one_week_ago"

    def test_absolute_date_string(self):
        result = date_filter("Due Date", "equals", "2026-05-14")
        assert result["date"]["equals"] == "2026-05-14"

    def test_empty_value(self):
        result = date_filter("Due Date", "is_not_empty")
        assert result["date"]["is_not_empty"] == {}

    def test_dict_value_passthrough(self):
        val = {"start": "2026-01-01", "end": "2026-12-31"}
        result = date_filter("Period", "equals", val)
        assert result["date"]["equals"] == val


class TestSelectFilter:
    def test_single_value(self):
        result = select_filter("Status", ["Active"])
        assert result["select"]["equals"] == "Active"

    def test_multi_value(self):
        result = select_filter("Priority", ["High", "Medium"])
        assert result["select"]["equals"] == ["High", "Medium"]

    def test_custom_match_type(self):
        result = select_filter("Status", ["Done"], match_type="does_not_equal")
        assert result["select"]["does_not_equal"] == "Done"


class TestMultiSelectFilter:
    def test_single_value(self):
        result = multi_select_filter("Tags", ["bug"])
        assert result["multi_select"]["contains"] == "bug"

    def test_multi_value(self):
        result = multi_select_filter("Tags", ["bug", "feature"])
        assert result["multi_select"]["contains"] == ["bug", "feature"]


class TestStatusFilter:
    def test_single_value(self):
        result = status_filter("Progress", ["In Progress"])
        assert result["status"]["equals"] == "In Progress"

    def test_multi_value(self):
        result = status_filter("Progress", ["Done", "Archived"])
        assert result["status"]["equals"] == ["Done", "Archived"]


class TestPeopleFilter:
    def test_me_default(self):
        result = people_filter("Assignee")
        assert result["people"]["contains"] == "me"

    def test_custom_user_id(self):
        result = people_filter("Owner", user_id="user-abc-123")
        assert result["people"]["contains"] == "user-abc-123"

    def test_does_not_contain(self):
        result = people_filter("Assignee", match_type="does_not_contain", user_id="me")
        assert result["people"]["does_not_contain"] == "me"


class TestCompoundFilter:
    def test_and_filter(self):
        conds = [
            select_filter("Status", ["Active"]),
            people_filter("Assignee"),
        ]
        result = compound_filter("and", conds)
        assert "and" in result
        assert len(result["and"]) == 2

    def test_or_filter(self):
        conds = [
            date_filter("Due", "is_not_empty"),
            status_filter("Status", ["Done"]),
        ]
        result = compound_filter("or", conds)
        assert "or" in result

    def test_invalid_operator(self):
        with pytest.raises(ValueError, match="Invalid operator"):
            compound_filter("xor", [])


# ============================================================
# widget_builder 테스트
# ============================================================


class TestChartWidget:
    def test_basic(self):
        w = chart_widget("매출 차트", chart_type="bar", property_name="amount")
        assert w["type"] == "chart"
        assert w["title"] == "매출 차트"
        assert w["chart_type"] == "bar"
        assert w["property"] == "amount"

    def test_with_position(self):
        pos = widget_position(row=0, col=0, width=2, height=1)
        w = chart_widget("차트", position=pos)
        assert w["position"]["width"] == 2


class TestNumberWidget:
    def test_basic(self):
        w = number_widget("총 건수", property_name="count_field", aggregation="sum")
        assert w["type"] == "number"
        assert w["aggregation"] == "sum"


class TestListWidget:
    def test_basic(self):
        w = list_widget("최근 항목", limit=3)
        assert w["type"] == "list"
        assert w["limit"] == 3

    def test_with_filters(self):
        f = {"property": "Status", "status": {"equals": "Active"}}
        w = list_widget("활성 항목", filters=f)
        assert w["filter"] == f


class TestFilteredViewWidget:
    def test_basic(self):
        w = filtered_view_widget("필터 뷰", view_type="board", limit=5)
        assert w["type"] == "filtered_view"
        assert w["view_type"] == "board"
        assert w["limit"] == 5


class TestWidgetPosition:
    def test_default(self):
        pos = widget_position()
        assert pos == {"row": 0, "col": 0, "width": 1, "height": 1}

    def test_custom(self):
        pos = widget_position(1, 2, 3, 2)
        assert pos == {"row": 1, "col": 2, "width": 3, "height": 2}


# ============================================================
# numbered_list 확장 테스트
# ============================================================


class TestNumberedListExtended:
    def test_default_no_format(self):
        result = numbered_list("항목")
        item = result["numbered_list_item"]
        assert "list_format" not in item
        assert "list_start_index" not in item

    def test_list_format_letters(self):
        result = numbered_list("a 항목", list_format="letters")
        assert result["numbered_list_item"]["list_format"] == "letters"

    def test_list_format_roman(self):
        result = numbered_list("i 항목", list_format="roman")
        assert result["numbered_list_item"]["list_format"] == "roman"

    def test_list_start_index(self):
        result = numbered_list("항목", list_start_index=5)
        assert result["numbered_list_item"]["list_start_index"] == 5

    def test_both_format_and_start(self):
        result = numbered_list("항목", list_format="numbers", list_start_index=10)
        item = result["numbered_list_item"]
        assert item["list_format"] == "numbers"
        assert item["list_start_index"] == 10

    def test_invalid_format_ignored(self):
        result = numbered_list("항목", list_format="invalid_format")
        assert "list_format" not in result["numbered_list_item"]


# ============================================================
# ViewOpsMixin 신규 메서드 테스트 (dashboard, form, view_query)
# ============================================================


def _make_mock_resp(data=None):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = data or {"id": "view-123", "type": "dashboard"}
    resp.text = ""
    return resp


def _make_mock_client(resp_data=None):
    from app.notion.view_ops import ViewOpsMixin

    client = MagicMock()
    client.mock_mode = False
    client._mock_id = MagicMock(return_value="mock-view-id")

    mock_resp = _make_mock_resp(resp_data)

    http = MagicMock()
    http.post = AsyncMock(return_value=mock_resp)
    http.get = AsyncMock(return_value=mock_resp)
    http.patch = AsyncMock(return_value=mock_resp)
    client._http_client = http

    rl = MagicMock()
    rl.acquire = AsyncMock()
    client.rate_limiter = rl

    client.get_data_source_id = AsyncMock(return_value="ds-abc-123")

    client.create_view = ViewOpsMixin.create_view.__get__(client, type(client))
    client.create_dashboard_view = ViewOpsMixin.create_dashboard_view.__get__(client, type(client))
    client.create_form_view = ViewOpsMixin.create_form_view.__get__(client, type(client))
    client.create_view_query = ViewOpsMixin.create_view_query.__get__(client, type(client))

    return client


class TestCreateDashboardView:
    @pytest.mark.asyncio
    async def test_dashboard_without_widgets(self):
        client = _make_mock_client()
        result = await client.create_dashboard_view(database_id="db-123", title="My Dashboard")
        assert result["id"] == "view-123"

    @pytest.mark.asyncio
    async def test_dashboard_with_widgets(self):
        client = _make_mock_client()
        widgets = [
            chart_widget("차트", chart_type="pie"),
            number_widget("총계", "amount", "sum"),
        ]
        await client.create_dashboard_view(database_id="db-123", widgets=widgets)
        call_args = client._http_client.post.call_args
        body = call_args.kwargs["json"]
        assert body["type"] == "dashboard"
        assert "configuration" in body
        assert body["configuration"]["widgets"] == widgets

    @pytest.mark.asyncio
    async def test_dashboard_mock_mode(self):
        client = _make_mock_client()
        client.mock_mode = True
        result = await client.create_dashboard_view(database_id="db-123")
        assert result["type"] == "dashboard"


class TestCreateFormView:
    @pytest.mark.asyncio
    async def test_form_default_disabled(self):
        client = _make_mock_client(resp_data={"id": "form-1", "type": "form"})
        await client.create_form_view(database_id="db-123")
        call_args = client._http_client.post.call_args
        body = call_args.kwargs["json"]
        assert body["type"] == "form"
        assert "configuration" not in body

    @pytest.mark.asyncio
    async def test_form_by_anyone(self):
        client = _make_mock_client(resp_data={"id": "form-1", "type": "form"})
        await client.create_form_view(
            database_id="db-123",
            submission_permissions="by_anyone",
            description="피드백을 입력하세요",
        )
        call_args = client._http_client.post.call_args
        body = call_args.kwargs["json"]
        assert body["configuration"]["submission_permissions"]["type"] == "by_anyone"
        assert body["configuration"]["description"] == "피드백을 입력하세요"

    @pytest.mark.asyncio
    async def test_form_with_cover(self):
        client = _make_mock_client(resp_data={"id": "form-1", "type": "form"})
        await client.create_form_view(
            database_id="db-123",
            cover_url="https://example.com/cover.jpg",
        )
        call_args = client._http_client.post.call_args
        body = call_args.kwargs["json"]
        assert body["configuration"]["cover"]["external"]["url"] == "https://example.com/cover.jpg"


class TestCreateViewQuery:
    @pytest.mark.asyncio
    async def test_basic_query(self):
        client = _make_mock_client(resp_data={"id": "query-1", "results": [{"id": "page-1"}]})
        result = await client.create_view_query(view_id="view-123", page_size=25)
        assert result["results"][0]["id"] == "page-1"
        call_args = client._http_client.post.call_args
        assert "/views/view-123/queries" in str(call_args)
        body = call_args.kwargs["json"]
        assert body["page_size"] == 25

    @pytest.mark.asyncio
    async def test_query_with_filters(self):
        client = _make_mock_client(resp_data={"id": "q-1", "results": []})
        f = status_filter("Status", ["Done"])
        await client.create_view_query(view_id="view-123", filters=f)
        call_args = client._http_client.post.call_args
        body = call_args.kwargs["json"]
        assert body["filter"] == f

    @pytest.mark.asyncio
    async def test_query_mock_mode(self):
        client = _make_mock_client()
        client.mock_mode = True
        result = await client.create_view_query(view_id="view-123")
        assert result["results"] == []

    @pytest.mark.asyncio
    async def test_query_error_fallback(self):
        from app.notion.view_ops import ViewOpsMixin

        error_resp = _make_mock_resp()
        error_resp.status_code = 400
        error_resp.text = "Bad Request"
        client = _make_mock_client()
        client._http_client.post = AsyncMock(return_value=error_resp)
        client.create_view_query = ViewOpsMixin.create_view_query.__get__(client, type(client))
        result = await client.create_view_query(view_id="view-bad")
        assert result["results"] == []


# ============================================================
# database_ops query_database 확장 (filter_properties, request_status) 테스트
# ============================================================


def _make_db_mock_client(resp_data=None):
    from app.notion.database_ops import DatabaseOpsMixin

    client = MagicMock()
    client.mock_mode = False

    mock_resp = _make_mock_resp(resp_data or {"results": [], "request_status": {"type": "complete"}})

    http = MagicMock()
    http.post = AsyncMock(return_value=mock_resp)
    client._http_client = http

    rl = MagicMock()
    rl.acquire = AsyncMock()
    client.rate_limiter = rl

    client.get_data_source_id = AsyncMock(return_value="ds-abc-123")
    client.query_database = DatabaseOpsMixin.query_database.__get__(client, type(client))

    return client


class TestQueryDatabaseExtended:
    @pytest.mark.asyncio
    async def test_filter_properties_sent(self):
        client = _make_db_mock_client()
        await client.query_database(
            database_id="db-123",
            filter_properties=["Name", "Status"],
        )
        call_args = client._http_client.post.call_args
        body = call_args.kwargs["json"]
        assert body["filter_properties"] == ["Name", "Status"]

    @pytest.mark.asyncio
    async def test_request_status_incomplete_logged(self):
        client = _make_db_mock_client(
            resp_data={
                "results": [{"id": "p-1"}],
                "request_status": {"type": "incomplete", "incomplete_reason": "max_page_size"},
            }
        )
        result = await client.query_database(database_id="db-123")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_uses_data_source_endpoint(self):
        client = _make_db_mock_client()
        await client.query_database(database_id="db-123")
        call_args = client._http_client.post.call_args
        assert "/data_sources/ds-abc-123/query" in str(call_args)


# ============================================================
# page_ops / database_ops template_id 파라미터 테스트
# ============================================================


def _make_page_mock_client():
    from app.notion.page_ops import PageOpsMixin

    client = MagicMock()
    client.mock_mode = False

    mock_resp = _make_mock_resp({"id": "page-1"})

    http = MagicMock()
    http.post = AsyncMock(return_value=mock_resp)
    client._http_client = http
    client._http_client_legacy = http

    rl = MagicMock()
    rl.acquire = AsyncMock()
    client.rate_limiter = rl

    client.create_page = PageOpsMixin.create_page.__get__(client, type(client))

    return client


def _make_dbitem_mock_client():
    from app.notion.database_ops import DatabaseOpsMixin

    client = MagicMock()
    client.mock_mode = False

    mock_resp = _make_mock_resp({"id": "item-1"})

    http = MagicMock()
    http.post = AsyncMock(return_value=mock_resp)
    client._http_client = http
    client._http_client_legacy = http

    rl = MagicMock()
    rl.acquire = AsyncMock()
    client.rate_limiter = rl

    client.add_database_item = DatabaseOpsMixin.add_database_item.__get__(client, type(client))

    return client


class TestTemplateIdSupport:
    @pytest.mark.asyncio
    async def test_create_page_with_template(self):
        client = _make_page_mock_client()
        await client.create_page(
            parent_id="parent-1",
            title="템플릿 적용 페이지",
            template_id="tmpl-abc",
        )
        call_args = client._http_client.post.call_args
        body = call_args.kwargs["json"]
        assert body["template"]["type"] == "template_id"
        assert body["template"]["template_id"] == "tmpl-abc"

    @pytest.mark.asyncio
    async def test_create_page_without_template(self):
        client = _make_page_mock_client()
        await client.create_page(parent_id="parent-1", title="일반 페이지")
        call_args = client._http_client.post.call_args
        body = call_args.kwargs["json"]
        assert "template" not in body

    @pytest.mark.asyncio
    async def test_add_db_item_with_template(self):
        client = _make_dbitem_mock_client()
        await client.add_database_item(
            database_id="db-123",
            properties={"Name": {"title": [{"text": {"content": "test"}}]}},
            template_id="tmpl-xyz",
        )
        call_args = client._http_client.post.call_args
        body = call_args.kwargs["json"]
        assert body["template"]["template_id"] == "tmpl-xyz"
