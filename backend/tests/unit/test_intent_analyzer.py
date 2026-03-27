"""Intent Analyzer 단위 테스트"""
import pytest
from app.agent.intent_analyzer import _mock_analyze


def test_create_dashboard():
    result = _mock_analyze("프로젝트 관리 대시보드 만들어줘")
    assert result.intent == "CREATE"
    assert result.template_type == "dashboard"
    assert result.confidence >= 0.8


def test_create_tracker():
    result = _mock_analyze("습관 트래커 만들어줘")
    assert result.intent == "CREATE"
    assert result.template_type == "tracker"


def test_color_blue():
    result = _mock_analyze("하늘색으로 만들어줘")
    assert result.color_theme == "blue"


def test_color_orange():
    result = _mock_analyze("주황색으로 대시보드 만들어줘")
    assert result.color_theme == "orange"


def test_color_green():
    result = _mock_analyze("초록색 트래커")
    assert result.color_theme == "green"


def test_ambiguous_request():
    result = _mock_analyze("노션 만들어줘")
    assert result.template_type == "custom"
    assert result.confidence < 0.7


def test_modify_intent():
    result = _mock_analyze("DB에 태그 속성 추가해줘")
    assert result.intent == "MODIFY"


def test_question_intent():
    result = _mock_analyze("버튼 추가 가능해?")
    assert result.intent == "QUESTION"


def test_bookmark_type():
    result = _mock_analyze("북마크 사이트 만들어줘")
    assert result.template_type == "bookmark"


def test_onboarding_type():
    result = _mock_analyze("신입사원 온보딩 가이드 만들어줘")
    assert result.template_type == "onboarding"


def test_sub_pages_extraction():
    result = _mock_analyze("대시보드 만들어줘 하위 페이지 3개 (ETC, Project, Study)")
    assert result.sub_pages is not None
    assert len(result.sub_pages) == 3
