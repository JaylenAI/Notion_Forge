"""number 속성 통화/퍼센트 포맷 (QUAL-6) 테스트."""

from app.notion.block_builder import _safe_number_format, build_database_properties


def test_safe_number_format_valid():
    assert _safe_number_format("won") == "won"
    assert _safe_number_format("percent") == "percent"
    assert _safe_number_format("dollar") == "dollar"


def test_safe_number_format_aliases():
    assert _safe_number_format("원") == "won"
    assert _safe_number_format("%") == "percent"
    assert _safe_number_format("KRW") == "won"


def test_safe_number_format_invalid_falls_back():
    assert _safe_number_format("bitcoin") == "number"
    assert _safe_number_format("") == "number"


def test_build_properties_applies_number_format():
    props = build_database_properties(
        {
            "이름": "title",
            "금액": {"type": "number", "format": "won"},
            "달성률": {"type": "number", "format": "%"},
            "그냥숫자": "number",
        }
    )
    assert props["금액"]["number"]["format"] == "won"
    assert props["달성률"]["number"]["format"] == "percent"
    # 포맷 미지정 number는 빈 config (기본)
    assert props["그냥숫자"]["number"] == {}
