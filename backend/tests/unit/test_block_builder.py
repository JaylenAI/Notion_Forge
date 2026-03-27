"""Block Builder 단위 테스트"""
from app.notion.block_builder import (
    heading, paragraph, callout, toggle, to_do, divider,
    bulleted_list, column_list, build_database_properties,
)


def test_heading():
    block = heading("Test", level=1, color="blue_background")
    assert block["type"] == "heading_1"
    assert block["heading_1"]["color"] == "blue_background"


def test_paragraph():
    block = paragraph("Hello")
    assert block["type"] == "paragraph"
    assert block["paragraph"]["rich_text"][0]["text"]["content"] == "Hello"


def test_callout():
    block = callout("Note", icon="📌", color="green_background")
    assert block["type"] == "callout"
    assert block["callout"]["icon"]["emoji"] == "📌"
    assert block["callout"]["color"] == "green_background"


def test_toggle():
    block = toggle("FAQ", children=[paragraph("Answer")])
    assert block["type"] == "toggle"
    assert len(block["toggle"]["children"]) == 1


def test_to_do():
    block = to_do("Task", checked=True)
    assert block["to_do"]["checked"] is True


def test_divider():
    block = divider()
    assert block["type"] == "divider"


def test_bulleted_list():
    block = bulleted_list("Item")
    assert block["type"] == "bulleted_list_item"


def test_column_list():
    block = column_list([[paragraph("Left")], [paragraph("Right")]])
    assert block["type"] == "column_list"
    assert len(block["column_list"]["children"]) == 2


def test_build_database_properties_simple():
    props = build_database_properties({"이름": "title", "완료": "checkbox"})
    assert props["이름"] == {"title": {}}
    assert props["완료"] == {"checkbox": {}}


def test_build_database_properties_select():
    props = build_database_properties({
        "카테고리": {"type": "select", "options": [{"name": "A", "color": "blue"}]}
    })
    assert props["카테고리"]["select"]["options"][0]["name"] == "A"
    assert props["카테고리"]["select"]["options"][0]["color"] == "blue"
