"""Blueprint Generator 단위 테스트 (dev-2: async + skill based)"""
import pytest
from app.agent.blueprint_generator import generate_blueprint, _mock_call, _assemble_blueprint


def test_mock_call_dashboard():
    result = _mock_call("프로젝트 대시보드 만들어줘")
    assert result["skill"] in ("manage", "hub")


def test_mock_call_tracker():
    result = _mock_call("습관 트래커 만들어줘")
    assert result["skill"] == "track"


def test_mock_call_bookmark():
    result = _mock_call("북마크 사이트 만들어줘")
    assert result["skill"] == "organize"


def test_mock_call_onboarding():
    result = _mock_call("온보딩 가이드 만들어줘")
    assert result["skill"] == "guide"


def test_mock_call_color():
    result = _mock_call("보라색으로 만들어줘")
    assert result["color"] == "purple"


def test_assemble_track():
    content = _mock_call("운동 기록 만들어줘")
    bp = _assemble_blueprint(content, None)
    assert bp["version"] == "2.0"
    assert len(bp["databases"]) >= 1
    assert any(b["type"] == "callout" for b in bp["blocks"])


def test_assemble_has_database():
    content = {"skill": "track", "title": "Test", "icon": "📋", "color": "blue",
               "callout_text": "테스트", "db_name": "DB", 
               "db_properties": {"이름": "title", "날짜": "date"},
               "views": ["calendar"], "sample_items": [{"이름": "항목1", "icon": "📌"}],
               "sub_pages": [], "faq": []}
    bp = _assemble_blueprint(content, None)
    assert len(bp["databases"]) == 1
    assert bp["databases"][0]["title"] == "DB"


@pytest.mark.asyncio
async def test_generate_blueprint_async():
    """generate_blueprint는 async 함수"""
    bp = await generate_blueprint("트래커 만들어줘")
    assert bp["version"] == "2.0"
    assert "metadata" in bp
    assert "databases" in bp
