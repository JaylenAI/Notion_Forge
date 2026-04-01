"""Blueprint Generator 단위 테스트 (v3: AI 자유 설계)"""
import pytest
from app.agent.blueprint_generator import generate_blueprint, _smart_fallback, _assemble_blueprint


def test_fallback_exercise():
    result = _smart_fallback("운동 기록 만들어줘")
    assert result["skill"] == "track"
    assert len(result["databases"]) >= 1
    assert len(result["databases"][0]["sample_items"]) >= 5


def test_fallback_reading():
    result = _smart_fallback("독서 기록 만들어줘")
    assert result["skill"] == "collect"
    assert len(result["databases"]) >= 1


def test_fallback_project():
    result = _smart_fallback("프로젝트 보드 만들어줘")
    assert result["skill"] == "manage"
    assert len(result["databases"]) >= 1


def test_fallback_has_blocks():
    result = _smart_fallback("운동 기록 만들어줘")
    assert len(result.get("blocks", [])) >= 3


def test_fallback_has_views():
    result = _smart_fallback("프로젝트 보드 만들어줘")
    db = result["databases"][0]
    assert len(db.get("views", [])) >= 2


def test_fallback_not_generic():
    result = _smart_fallback("운동 기록 만들어줘")
    first_item = result["databases"][0]["sample_items"][0]
    title_key = list(first_item.keys())[0]
    assert "항목" not in first_item[title_key]


def test_assemble_creates_blueprint():
    content = _smart_fallback("운동 기록 만들어줘")
    bp = _assemble_blueprint(content)
    assert bp["version"] == "3.0"
    assert len(bp["databases"]) >= 1
    assert len(bp["blocks"]) >= 3


@pytest.mark.asyncio
async def test_generate_blueprint_async():
    bp = await generate_blueprint("트래커 만들어줘")
    assert bp["version"] == "3.0"
    assert len(bp["databases"]) >= 1
