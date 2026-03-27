"""Blueprint Generator 단위 테스트"""
from app.agent.blueprint_generator import generate_blueprint
from app.schemas.blueprint import IntentResult


def test_dashboard_blueprint():
    intent = IntentResult(intent="CREATE", template_type="dashboard", title="대시보드", color_theme="orange", confidence=0.9)
    bp = generate_blueprint(intent)
    assert bp["metadata"]["template_type"] == "dashboard"
    assert bp["metadata"]["color_theme"] == "orange"
    assert bp["main_page"]["icon"] == "🏢"
    assert len(bp["databases"]) >= 1


def test_tracker_blueprint():
    intent = IntentResult(intent="CREATE", template_type="tracker", title="트래커", color_theme="green", confidence=0.9)
    bp = generate_blueprint(intent)
    assert bp["metadata"]["template_type"] == "tracker"
    assert len(bp["databases"]) >= 1
    assert any(b["type"] == "callout" for b in bp["blocks"])


def test_bookmark_blueprint():
    intent = IntentResult(intent="CREATE", template_type="bookmark", title="북마크", confidence=0.9)
    bp = generate_blueprint(intent)
    assert len(bp["databases"]) >= 1
    db_props = bp["databases"][0]["properties"]
    assert "URL" in db_props or "url" in str(db_props).lower()


def test_onboarding_blueprint():
    intent = IntentResult(intent="CREATE", template_type="onboarding", title="온보딩", color_theme="blue", confidence=0.9)
    bp = generate_blueprint(intent)
    assert any(b["type"] == "to_do" for b in bp["blocks"])


def test_custom_blueprint():
    intent = IntentResult(intent="CREATE", template_type="custom", title="커스텀", confidence=0.5)
    bp = generate_blueprint(intent)
    assert bp["main_page"]["icon"] == "⚡"


def test_sub_pages():
    intent = IntentResult(intent="CREATE", template_type="dashboard", title="대시보드", sub_pages=["A", "B"], confidence=0.9)
    bp = generate_blueprint(intent)
    assert len(bp["sub_pages"]) >= 2


def test_note_blueprint_has_sub_pages():
    intent = IntentResult(intent="CREATE", template_type="note", title="Tea Note", color_theme="green", confidence=0.9)
    bp = generate_blueprint(intent)
    assert len(bp["sub_pages"]) >= 1
