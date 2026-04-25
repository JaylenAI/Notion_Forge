"""DocumentParser 테스트: 문서 파싱 함수 검증"""

from app.agent.document_parser import (
    _parse_csv,
    _parse_markdown,
    _parse_text,
    parse_document,
    parse_pdf_bytes,
)


class TestParseDocument:
    def test_csv_dispatch(self):
        result = parse_document("이름,상태\nA,완료", "data.csv")
        assert "properties" in result

    def test_md_dispatch(self):
        result = parse_document("# 제목\n내용", "doc.md")
        assert "blocks" in result

    def test_txt_dispatch(self):
        result = parse_document("일반 텍스트", "note.txt")
        assert "text_content" in result

    def test_no_extension_defaults_to_txt(self):
        result = parse_document("텍스트", "noext")
        assert "text_content" in result


class TestParseCSV:
    def test_empty_csv(self):
        result = _parse_csv("")
        assert result["hint"] == "빈 CSV 파일"

    def test_headers_detected(self):
        result = _parse_csv("이름,날짜,금액,상태,이메일,url,체크\na,2026-01-01,100,완료,a@b.com,http://x,Y")
        assert result["properties"]["이름"] == "title"
        assert result["properties"]["날짜"] == "date"
        assert result["properties"]["금액"] == "number"
        assert result["properties"]["상태"] == "status"
        assert result["properties"]["이메일"] == "email"
        assert result["properties"]["url"] == "url"
        assert result["properties"]["체크"] == "checkbox"

    def test_fallback_to_rich_text(self):
        result = _parse_csv("기타\nval")
        assert result["properties"]["기타"] == "rich_text"

    def test_sample_items_max_5(self):
        rows = "이름\n" + "\n".join(f"item{i}" for i in range(10))
        result = _parse_csv(rows)
        assert len(result["sample_items"]) == 5

    def test_hint_format(self):
        result = _parse_csv("A,B\n1,2\n3,4")
        assert "2개 컬럼" in result["hint"]
        assert "2개 행" in result["hint"]

    def test_db_title_present(self):
        result = _parse_csv("이름\nA")
        assert result["db_title"] == "Imported Data"


class TestParseMarkdown:
    def test_heading_levels(self):
        result = _parse_markdown("# H1\n## H2\n### H3")
        assert result["blocks"][0]["type"] == "heading_1"
        assert result["blocks"][1]["type"] == "heading_2"
        assert result["blocks"][2]["type"] == "heading_3"

    def test_bulleted_list(self):
        result = _parse_markdown("- 항목A\n* 항목B")
        assert all(b["type"] == "bulleted_list" for b in result["blocks"])

    def test_numbered_list(self):
        result = _parse_markdown("1. 첫 번째\n2. 두 번째")
        assert all(b["type"] == "numbered_list" for b in result["blocks"])

    def test_checkbox(self):
        result = _parse_markdown("- [ ] 할 일\n- [x] 완료")
        assert result["blocks"][0]["type"] == "to_do"
        assert result["blocks"][0]["checked"] is False
        assert result["blocks"][1]["checked"] is True

    def test_quote(self):
        result = _parse_markdown("> 인용문")
        assert result["blocks"][0]["type"] == "quote"

    def test_code_fence_becomes_divider(self):
        result = _parse_markdown("```python\ncode\n```")
        assert any(b["type"] == "divider" for b in result["blocks"])

    def test_horizontal_rule(self):
        for rule in ("---", "***", "___"):
            result = _parse_markdown(rule)
            assert result["blocks"][0]["type"] == "divider"

    def test_paragraph(self):
        result = _parse_markdown("일반 텍스트")
        assert result["blocks"][0]["type"] == "paragraph"

    def test_empty_lines_skipped(self):
        result = _parse_markdown("텍스트\n\n\n다른 텍스트")
        assert len(result["blocks"]) == 2

    def test_hint_format(self):
        result = _parse_markdown("# 제목\n내용")
        assert "2개 블록" in result["hint"]


class TestParseText:
    def test_basic_text(self):
        result = _parse_text("줄1\n줄2\n줄3")
        assert "3줄" in result["hint"]
        assert "줄1" in result["text_content"]

    def test_empty_lines_excluded(self):
        result = _parse_text("줄1\n\n\n줄2")
        assert "2줄" in result["hint"]

    def test_max_30_lines(self):
        content = "\n".join(f"줄{i}" for i in range(50))
        result = _parse_text(content)
        assert result["text_content"].count("\n") <= 29


class TestParsePDF:
    def test_pymupdf_not_installed(self):
        result = parse_pdf_bytes(b"fake pdf content")
        assert "PyMuPDF" in result["hint"] or "파싱 실패" in result["hint"]
