"""Intent Analyzer 단위 테스트"""

from app.agent.intent_analyzer import (
    COLOR_MAP,
    TYPE_KEYWORDS,
    _extract_sub_pages,
    _mock_analyze,
    _override_intent,
    _parse_ai_response,
)


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


class TestOverrideIntent:
    def test_create_keyword_overrides_question(self):
        assert _override_intent("갤러리 뷰로 만들어줘", "QUESTION") == "CREATE"

    def test_no_create_keyword_keeps_question(self):
        assert _override_intent("버튼 추가 가능해?", "QUESTION") == "QUESTION"

    def test_create_stays_create(self):
        assert _override_intent("대시보드 만들어줘", "CREATE") == "CREATE"

    def test_complex_prompt_with_create(self):
        msg = "콘텐츠 크리에이터용 채널 운영 시스템 만들어줘. 갤러리 뷰로 보여줘."
        assert _override_intent(msg, "QUESTION") == "CREATE"

    def test_mock_complex_create_prompt(self):
        msg = "영상 기획 DB 갤러리 뷰로 만들어줘. 수익 관리 DB도 필요해."
        result = _mock_analyze(msg)
        assert result.intent == "CREATE"

    def test_modify_keeps_modify(self):
        assert _override_intent("항목 추가해줘", "MODIFY") == "MODIFY"

    def test_both_create_and_modify_keeps_original(self):
        assert _override_intent("만들어서 추가해줘", "MODIFY") == "MODIFY"


class TestParseAIResponse:
    def test_valid_json(self):
        text = '{"intent": "CREATE", "template_type": "dashboard", "confidence": 0.9, "title": "테스트"}'
        result = _parse_ai_response(text)
        assert result.intent == "CREATE"
        assert result.template_type == "dashboard"

    def test_json_with_surrounding_text(self):
        text = 'Here is the result: {"intent": "CREATE", "template_type": "project", "confidence": 0.8} done.'
        result = _parse_ai_response(text)
        assert result.intent == "CREATE"

    def test_no_json_returns_question(self):
        result = _parse_ai_response("no json here")
        assert result.intent == "QUESTION"
        assert result.confidence == 0.3

    def test_empty_title_gets_default(self):
        text = '{"intent": "CREATE", "template_type": "dashboard", "confidence": 0.9, "title": ""}'
        result = _parse_ai_response(text)
        assert result.title == "대시보드"

    def test_empty_title_project_default(self):
        text = '{"intent": "CREATE", "template_type": "project", "confidence": 0.9, "title": ""}'
        result = _parse_ai_response(text)
        assert result.title == "프로젝트 보드"


class TestColorMapAndTypeKeywords:
    def test_color_map_has_korean_entries(self):
        assert COLOR_MAP["보라색"] == "purple"
        assert COLOR_MAP["핑크"] == "pink"
        assert COLOR_MAP["노란색"] == "yellow"
        assert COLOR_MAP["회색"] == "gray"

    def test_type_keywords_crm(self):
        assert "crm" in TYPE_KEYWORDS
        assert "고객" in TYPE_KEYWORDS["crm"]

    def test_type_keywords_note(self):
        assert "note" in TYPE_KEYWORDS
        assert "노트" in TYPE_KEYWORDS["note"]


class TestExtractSubPages:
    def test_parenthesized_format(self):
        result = _extract_sub_pages("하위 페이지 3개 (가이드, FAQ, 일정)")
        assert len(result) == 3

    def test_colon_format(self):
        result = _extract_sub_pages("하위 페이지: 가이드, FAQ")
        assert len(result) == 2

    def test_no_sub_pages(self):
        result = _extract_sub_pages("대시보드 만들어줘")
        assert result == []


class TestMockAnalyzeEdgeCases:
    def test_crm_type(self):
        result = _mock_analyze("CRM 고객 관리 만들어줘")
        assert result.template_type == "crm"
        assert result.title == "CRM"

    def test_note_type(self):
        result = _mock_analyze("독서 노트 만들어줘")
        assert result.template_type == "note"

    def test_color_purple(self):
        result = _mock_analyze("보라색 대시보드 만들어")
        assert result.color_theme == "purple"

    def test_delete_is_modify(self):
        result = _mock_analyze("이 항목 삭제해줘")
        assert result.intent == "MODIFY"
