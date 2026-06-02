"""품질 회귀 게이트 (Phase 5/C2) — 큐레이션 recipe가 품질 밴드 아래로 떨어지면 CI 실패.

엔진/루브릭 변경이 기존 우수 예시 품질을 떨어뜨리는 회귀를 자동 차단한다.
"""

import json
from pathlib import Path

import pytest

from app.agent.premium_rubric import score_blueprint

RECIPES_DIR = Path(__file__).resolve().parents[3] / "recipes"
_RECIPES = sorted(RECIPES_DIR.glob("*.json")) if RECIPES_DIR.exists() else []


@pytest.mark.parametrize("recipe_file", _RECIPES, ids=lambda p: p.stem)
def test_recipe_quality_does_not_regress(recipe_file):
    data = json.loads(recipe_file.read_text(encoding="utf-8"))
    bp = data.get("blueprint", data)
    result = score_blueprint(bp)
    # advanced 우수 예시(crm/okr)는 프리미엄($50+ = 75) 유지, 그 외는 최소 판매가능선(40) 유지
    floor = 75 if data.get("complexity") == "advanced" else 40
    assert result.score >= floor, (
        f"{recipe_file.stem}: 유료급 {result.score} < 기준 {floor} ({result.band_price}) — 품질 회귀 발생"
    )


def test_recipes_present():
    # recipe 코퍼스가 사라지면(게이트 무력화) 알아채도록
    assert len(_RECIPES) >= 3
