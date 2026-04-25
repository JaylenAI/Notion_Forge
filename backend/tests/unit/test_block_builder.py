"""BlockBuilder 단위 테스트: 블록 타입별 Notion API JSON 출력 검증"""

from app.notion.block_builder import (
    _safe_color,
    audio,
    bookmark,
    breadcrumb,
    build_database_properties,
    bulleted_list,
    button,
    callout,
    code_block,
    column_list,
    divider,
    embed,
    equation_block,
    file_block,
    heading,
    icon_emoji,
    icon_external,
    icon_native,
    image,
    link_to_database,
    link_to_page,
    mention_date,
    mention_page,
    numbered_list,
    paragraph,
    pdf,
    quote,
    rich_text,
    rich_text_array,
    rich_text_equation,
    rich_text_mention_database,
    rich_text_mention_date,
    rich_text_mention_page,
    rich_text_mention_user,
    rich_text_template_mention,
    synced_block_duplicate,
    synced_block_original,
    table,
    table_of_contents,
    to_do,
    toggle,
    video,
)


class TestSafeColor:
    def test_valid_color(self):
        assert _safe_color("blue") == "blue"
        assert _safe_color("red_background") == "red_background"

    def test_invalid_color_returns_default(self):
        assert _safe_color("rainbow") == "default"
        assert _safe_color("") == "default"


class TestRichText:
    def test_plain_text(self):
        result = rich_text("hello")
        assert len(result) == 1
        assert result[0]["text"]["content"] == "hello"
        assert result[0]["annotations"]["bold"] is False

    def test_bold_text(self):
        result = rich_text("bold", bold=True)
        assert result[0]["annotations"]["bold"] is True

    def test_all_annotations(self):
        result = rich_text(
            "styled", bold=True, italic=True, underline=True, strikethrough=True, code=True, color="blue"
        )
        ann = result[0]["annotations"]
        assert all(ann[k] is True for k in ["bold", "italic", "underline", "strikethrough", "code"])
        assert ann["color"] == "blue"

    def test_with_link(self):
        result = rich_text("click", link="https://example.com")
        assert result[0]["text"]["link"]["url"] == "https://example.com"

    def test_invalid_color_normalized(self):
        result = rich_text("test", color="invalid")
        assert result[0]["annotations"]["color"] == "default"


class TestRichTextArray:
    def test_mixed_segments(self):
        result = rich_text_array(
            [
                {"text": "볼드", "bold": True},
                {"text": " 일반 "},
                {"text": "링크", "link": "https://test.com"},
            ]
        )
        assert len(result) == 3
        assert result[0]["annotations"]["bold"] is True
        assert result[2]["text"]["link"]["url"] == "https://test.com"


class TestRichTextSpecial:
    def test_equation(self):
        result = rich_text_equation("E = mc^2")
        assert result[0]["type"] == "equation"

    def test_mention_page(self):
        result = rich_text_mention_page("page-id-123")
        assert result[0]["type"] == "mention"

    def test_mention_date(self):
        result = rich_text_mention_date("2026-01-01", "2026-01-31")
        assert result[0]["mention"]["date"]["start"] == "2026-01-01"
        assert result[0]["mention"]["date"]["end"] == "2026-01-31"

    def test_mention_date_no_end(self):
        result = rich_text_mention_date("2026-01-01")
        assert "end" not in result[0]["mention"]["date"]

    def test_mention_user(self):
        result = rich_text_mention_user("user-id")
        assert result[0]["mention"]["user"]["id"] == "user-id"

    def test_mention_database(self):
        result = rich_text_mention_database("db-id")
        assert result[0]["mention"]["database"]["id"] == "db-id"

    def test_template_mention(self):
        result = rich_text_template_mention("today")
        assert result[0]["type"] == "mention"


class TestBlockBuilders:
    def test_heading_1(self):
        result = heading("제목", level=1)
        assert result["type"] == "heading_1"
        assert result["heading_1"]["rich_text"][0]["text"]["content"] == "제목"

    def test_heading_2_with_color(self):
        result = heading("섹션", level=2, color="blue")
        assert result["type"] == "heading_2"
        assert result["heading_2"]["color"] == "blue"

    def test_heading_3_toggleable(self):
        result = heading("토글", level=3, is_toggleable=True)
        assert result["heading_3"]["is_toggleable"] is True

    def test_heading_default_level(self):
        result = heading("제목", level=1, color="blue_background")
        assert result["type"] == "heading_1"
        assert result["heading_1"]["color"] == "blue_background"

    def test_paragraph(self):
        result = paragraph("내용")
        assert result["type"] == "paragraph"
        assert result["paragraph"]["rich_text"][0]["text"]["content"] == "내용"

    def test_callout_basic(self):
        result = callout("환영!", icon="👋", color="blue_background")
        assert result["type"] == "callout"
        assert result["callout"]["icon"]["emoji"] == "👋"
        assert result["callout"]["color"] == "blue_background"

    def test_callout_with_children(self):
        child = paragraph("자식 블록")
        result = callout("부모", children=[child])
        assert len(result["callout"]["children"]) == 1

    def test_toggle_basic(self):
        result = toggle("토글 제목")
        assert result["type"] == "toggle"

    def test_toggle_with_children(self):
        result = toggle("토글", children=[paragraph("내용")])
        assert len(result["toggle"]["children"]) == 1

    def test_to_do_checked(self):
        result = to_do("할 일", checked=True)
        assert result["to_do"]["checked"] is True

    def test_to_do_unchecked(self):
        result = to_do("할 일")
        assert result["to_do"]["checked"] is False

    def test_divider(self):
        result = divider()
        assert result["type"] == "divider"

    def test_bulleted_list(self):
        result = bulleted_list("항목")
        assert result["type"] == "bulleted_list_item"

    def test_bulleted_list_with_children(self):
        result = bulleted_list("항목", children=[bulleted_list("하위")])
        assert "children" in result["bulleted_list_item"]

    def test_numbered_list(self):
        result = numbered_list("항목")
        assert result["type"] == "numbered_list_item"

    def test_quote_basic(self):
        result = quote("인용")
        assert result["type"] == "quote"

    def test_quote_with_children(self):
        result = quote("인용", children=[paragraph("출처")])
        assert "children" in result["quote"]


class TestTableBlock:
    def test_basic_table(self):
        rows = [["이름", "나이"], ["홍길동", "30"]]
        result = table(rows)
        assert result["type"] == "table"
        assert result["table"]["table_width"] == 2
        assert result["table"]["has_column_header"] is True

    def test_table_with_row_header(self):
        rows = [["A", "B"], ["C", "D"]]
        result = table(rows, has_row_header=True)
        assert result["table"]["has_row_header"] is True

    def test_table_children_count(self):
        rows = [["H1", "H2"], ["R1C1", "R1C2"], ["R2C1", "R2C2"]]
        result = table(rows)
        assert len(result["table"]["children"]) == 3


class TestMediaBlocks:
    def test_bookmark(self):
        result = bookmark("https://example.com", caption="예시")
        assert result["type"] == "bookmark"
        assert result["bookmark"]["url"] == "https://example.com"

    def test_image(self):
        result = image("https://example.com/img.png", caption="이미지")
        assert result["type"] == "image"
        assert result["image"]["external"]["url"] == "https://example.com/img.png"

    def test_video(self):
        result = video("https://youtube.com/watch?v=test")
        assert result["type"] == "video"

    def test_audio(self):
        result = audio("https://example.com/audio.mp3")
        assert result["type"] == "audio"

    def test_file_block(self):
        result = file_block("https://example.com/doc.pdf", name="문서")
        assert result["type"] == "file"

    def test_pdf(self):
        result = pdf("https://example.com/doc.pdf")
        assert result["type"] == "pdf"

    def test_code_block(self):
        result = code_block("print('hello')", language="python")
        assert result["type"] == "code"
        assert result["code"]["language"] == "python"

    def test_embed(self):
        result = embed("https://twitter.com/test")
        assert result["type"] == "embed"
        assert result["embed"]["url"] == "https://twitter.com/test"


class TestAdvancedBlocks:
    def test_table_of_contents(self):
        result = table_of_contents(color="blue")
        assert result["type"] == "table_of_contents"

    def test_breadcrumb(self):
        result = breadcrumb()
        assert result["type"] == "breadcrumb"

    def test_equation_block(self):
        result = equation_block("x^2 + y^2 = r^2")
        assert result["type"] == "equation"

    def test_synced_block_original(self):
        children = [paragraph("동기화됨")]
        result = synced_block_original(children)
        assert result["type"] == "synced_block"
        assert result["synced_block"]["synced_from"] is None

    def test_synced_block_duplicate(self):
        result = synced_block_duplicate("original-id")
        assert result["synced_block"]["synced_from"]["block_id"] == "original-id"

    def test_column_list_basic(self):
        cols = [[paragraph("왼쪽")], [paragraph("오른쪽")]]
        result = column_list(cols)
        assert result["type"] == "column_list"
        assert len(result["column_list"]["children"]) == 2

    def test_link_to_page(self):
        result = link_to_page("page-id")
        assert result["type"] == "link_to_page"

    def test_link_to_database(self):
        result = link_to_database("db-id")
        assert result["type"] == "link_to_page"
        assert result["link_to_page"]["database_id"] == "db-id"

    def test_button(self):
        result = button("클릭", actions=[{"type": "open_url", "url": "https://test.com"}])
        assert result["type"] == "button"

    def test_mention_page_returns_mention(self):
        result = mention_page("page-id", text="링크")
        assert result["type"] == "mention"
        assert result["mention"]["page"]["id"] == "page-id"

    def test_mention_date_returns_mention(self):
        result = mention_date("2026-01-01")
        assert result["type"] == "mention"
        assert result["mention"]["date"]["start"] == "2026-01-01"


class TestIcons:
    def test_emoji(self):
        assert icon_emoji("📋") == {"type": "emoji", "emoji": "📋"}

    def test_external(self):
        result = icon_external("https://example.com/icon.png")
        assert result["type"] == "external"

    def test_native(self):
        result = icon_native("star", color="blue")
        assert result["type"] == "icon"
        assert result["icon"]["name"] == "star"


class TestBuildDatabaseProperties:
    def test_simple_string_props(self):
        result = build_database_properties({"이름": "title", "완료": "checkbox"})
        assert result["이름"] == {"title": {}}
        assert result["완료"] == {"checkbox": {}}

    def test_select_options_list(self):
        result = build_database_properties(
            {
                "이름": "title",
                "우선순위": {"type": "select", "options": ["높음", "중간", "낮음"]},
            }
        )
        opts = result["우선순위"]["select"]["options"]
        assert len(opts) == 3
        assert opts[0]["name"] == "높음"

    def test_select_options_dict(self):
        result = build_database_properties(
            {
                "이름": "title",
                "카테고리": {"type": "select", "options": [{"name": "A", "color": "blue"}]},
            }
        )
        assert result["카테고리"]["select"]["options"][0]["color"] == "blue"

    def test_multi_select(self):
        result = build_database_properties(
            {
                "이름": "title",
                "태그": {"type": "multi_select", "options": ["A", "B"]},
            }
        )
        assert "multi_select" in result["태그"]

    def test_number_type(self):
        result = build_database_properties(
            {
                "이름": "title",
                "금액": {"type": "number"},
            }
        )
        assert "number" in result["금액"]

    def test_formula(self):
        result = build_database_properties(
            {
                "이름": "title",
                "계산": {"type": "formula", "expression": 'prop("금액") * 1.1'},
            }
        )
        assert "formula" in result["계산"]

    def test_rich_text_type(self):
        result = build_database_properties({"이름": "title", "텍스트": "rich_text"})
        assert "rich_text" in result["텍스트"]

    def test_status_type(self):
        result = build_database_properties({"이름": "title", "상태": "status"})
        assert "status" in result["상태"]

    def test_date_type(self):
        result = build_database_properties({"이름": "title", "날짜": "date"})
        assert "date" in result["날짜"]

    def test_auto_title_when_missing(self):
        result = build_database_properties({"상태": "status", "날짜": "date"})
        assert result["상태"] == {"title": {}}
        assert "date" in result["날짜"]
