"""제목 정리(_clean_title) 테스트 — 색상/스타일 지시가 제목에 새어드는 버그 회귀 방지.

라이브 AI E2E에서 "운동 습관 트래커 만들어줘, 주황색으로" → 제목에 ", 주황색으로"가 남던 문제.
"""

from app.agent.blueprint_generator import _clean_title


def test_strips_color_directive():
    t = _clean_title("운동 습관 트래커 만들어줘, 주황색으로")
    assert "주황색" not in t
    assert "만들어줘" not in t
    assert "운동" in t and "트래커" in t


def test_strips_various_colors():
    for phrase, color in [
        ("프로젝트 보드 파란색으로", "파란색"),
        ("독서 기록, 초록색", "초록색"),
        ("가계부 만들어줘 핑크", "핑크"),
    ]:
        t = _clean_title(phrase)
        assert color not in t, f"{color} 가 제거되지 않음: {t!r}"


def test_keeps_clean_title_unchanged():
    assert _clean_title("독서 기록") == "독서 기록"


def test_strips_trailing_punctuation():
    t = _clean_title("운동 트래커 만들어줘!")
    assert not t.endswith(",")
    assert "!" not in t
    assert "운동" in t


def test_preserves_words_containing_color_substring():
    """색상어를 substring으로 포함하는 정상 단어는 보존돼야 한다 (WIRE-03 회귀)."""
    assert "블루베리" in _clean_title("블루베리 농장 관리")
    assert "그린팀" in _clean_title("그린팀 프로젝트 보드")
    assert "Evergreen" in _clean_title("Evergreen 독서 기록")
    assert "레드오션" in _clean_title("레드오션 분석 보드")
    assert "핑크퐁" in _clean_title("핑크퐁 콘텐츠 기획")
