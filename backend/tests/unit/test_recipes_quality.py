"""레시피 품질 회귀 게이트 — 실제 산출물(recipes/*.json)이 '유료 판매급' 기준을 충족하는지 검증.

Gate 2 QUAL-7/13: 마켓플레이스 상위급 품질의 핵심 지표를 코드로 고정한다.
- 구조 유효성 (main_page / blocks / databases / sample_items)
- relation target_db_index 범위 무결성
- P0 차별화 지표: business/advanced 레시피는 rollup 또는 formula(자동 집계/계산)를 포함해야 한다
"""

import json
from pathlib import Path

import pytest

RECIPES_DIR = Path(__file__).resolve().parents[3] / "recipes"
RECIPE_FILES = sorted(RECIPES_DIR.glob("*.json"))
RECIPE_IDS = [fp.stem for fp in RECIPE_FILES]


def _load(fp: Path) -> dict:
    return json.loads(fp.read_text(encoding="utf-8"))


def _db_props(db: dict) -> dict:
    """레시피는 'properties', 골든은 'db_properties' 키를 쓴다 — 둘 다 처리."""
    return db.get("properties") or db.get("db_properties") or {}


def _prop_types(db: dict) -> list[str]:
    """DB properties의 타입 목록 (문자열 단축형 + dict 형 모두 처리)."""
    types = []
    for spec in _db_props(db).values():
        if isinstance(spec, str):
            types.append(spec)
        elif isinstance(spec, dict):
            types.append(spec.get("type", ""))
    return types


def _all_prop_types(bp: dict) -> list[str]:
    out: list[str] = []
    for db in bp.get("databases", []):
        out.extend(_prop_types(db))
    return out


def test_recipes_exist():
    assert RECIPE_FILES, "recipes/ 에 레시피가 하나도 없습니다"


@pytest.mark.parametrize("fp", RECIPE_FILES, ids=RECIPE_IDS)
def test_recipe_valid_json(fp):
    data = _load(fp)
    assert data.get("id"), f"{fp.name}: id 누락"
    assert data.get("name"), f"{fp.name}: name 누락"
    bp = data.get("blueprint")
    assert isinstance(bp, dict), f"{fp.name}: blueprint 누락"
    assert bp.get("main_page", {}).get("title"), f"{fp.name}: main_page.title 누락"
    assert isinstance(bp.get("blocks"), list) and bp["blocks"], f"{fp.name}: blocks 비어있음"
    assert isinstance(bp.get("databases"), list) and bp["databases"], f"{fp.name}: databases 비어있음"


@pytest.mark.parametrize("fp", RECIPE_FILES, ids=RECIPE_IDS)
def test_recipe_databases_have_title_and_samples(fp):
    bp = _load(fp)["blueprint"]
    for db in bp["databases"]:
        types = _prop_types(db)
        assert "title" in types, f"{fp.name} / {db.get('title')}: title 속성 없음"
        samples = db.get("sample_items", [])
        assert len(samples) >= 3, f"{fp.name} / {db.get('title')}: 샘플 데이터 3개 미만 ({len(samples)})"


@pytest.mark.parametrize("fp", RECIPE_FILES, ids=RECIPE_IDS)
def test_recipe_relation_indices_valid(fp):
    bp = _load(fp)["blueprint"]
    db_count = len(bp["databases"])
    for db in bp["databases"]:
        for name, spec in db.get("properties", {}).items():
            if isinstance(spec, dict) and spec.get("type") == "relation":
                idx = spec.get("target_db_index")
                assert idx is not None, f"{fp.name}: relation '{name}' target_db_index 누락"
                assert 0 <= idx < db_count, f"{fp.name}: relation '{name}' target_db_index 범위 초과 ({idx})"


@pytest.mark.parametrize("fp", RECIPE_FILES, ids=RECIPE_IDS)
def test_recipe_rollup_formula_references_valid(fp):
    """rollup/formula가 참조하는 relation_property/prop이 실제 존재하는지 느슨하게 검증."""
    bp = _load(fp)["blueprint"]
    for db in bp["databases"]:
        prop_names = set(db.get("properties", {}).keys())
        for name, spec in db.get("properties", {}).items():
            if not isinstance(spec, dict):
                continue
            if spec.get("type") == "rollup":
                rel = spec.get("relation_property")
                assert rel in prop_names, f"{fp.name}: rollup '{name}' 의 relation_property '{rel}' 가 같은 DB에 없음"
                assert spec.get("function"), f"{fp.name}: rollup '{name}' function 누락"
            if spec.get("type") == "formula":
                assert spec.get("expression"), f"{fp.name}: formula '{name}' expression 누락"


# ── P0 차별화 게이트: business/advanced 는 자동 집계/계산을 포함해야 한다 ──

_PREMIUM_CATEGORIES = {"business"}


@pytest.mark.parametrize("fp", RECIPE_FILES, ids=RECIPE_IDS)
def test_premium_recipes_have_rollup_or_formula(fp):
    data = _load(fp)
    is_premium = data.get("category") in _PREMIUM_CATEGORIES or data.get("complexity") == "advanced"
    if not is_premium:
        pytest.skip("프리미엄(business/advanced) 레시피가 아님")
    types = _all_prop_types(data["blueprint"])
    assert "rollup" in types or "formula" in types, (
        f"{fp.name}: 유료급(business/advanced) 레시피는 rollup 또는 formula(자동 집계/계산)를 포함해야 합니다"
    )


def test_crm_dashboard_has_rollup():
    bp = _load(RECIPES_DIR / "crm-dashboard.json")["blueprint"]
    assert "rollup" in _all_prop_types(bp), "CRM 대시보드는 딜 집계 rollup을 포함해야 합니다"
    assert len(bp["databases"]) >= 2, "CRM은 멀티 DB(고객+딜)여야 합니다"


def test_project_board_has_formula():
    bp = _load(RECIPES_DIR / "project-board.json")["blueprint"]
    assert "formula" in _all_prop_types(bp), "프로젝트 보드는 D-Day formula를 포함해야 합니다"


# ── 골든 예시(AI 생성 가이드) 품질 검증 ──

GOLDEN_DIR = Path(__file__).resolve().parents[1].parent / "app" / "agent" / "prompts" / "golden"
GOLDEN_FILES = sorted(GOLDEN_DIR.glob("*.json"))
GOLDEN_IDS = [fp.stem for fp in GOLDEN_FILES]


@pytest.mark.parametrize("fp", GOLDEN_FILES, ids=GOLDEN_IDS)
def test_golden_valid_and_relation_integrity(fp):
    """골든 예시가 유효 JSON이고 relation 인덱스/rollup 참조가 무결한지 검증."""
    g = _load(fp)  # 골든은 blueprint 자체가 최상위
    dbs = g.get("databases", [])
    assert isinstance(dbs, list) and dbs, f"{fp.name}: databases 없음"
    for db in dbs:
        props = _db_props(db)
        prop_names = set(props.keys())
        for name, spec in props.items():
            if not isinstance(spec, dict):
                continue
            if spec.get("type") == "relation" and "target_db_index" in spec:
                idx = spec["target_db_index"]
                assert 0 <= idx < len(dbs), f"{fp.name}: relation '{name}' target_db_index 범위 초과"
            if spec.get("type") == "rollup":
                assert spec.get("relation_property") in prop_names, (
                    f"{fp.name}: rollup '{name}' relation_property 미존재"
                )


def test_golden_dashboard_widgets_has_rollup():
    """대시보드 골든은 AI에게 rollup 집계를 가르치는 레퍼런스여야 한다."""
    g = _load(GOLDEN_DIR / "dashboard_widgets.json")
    types = []
    for db in g.get("databases", []):
        types.extend(_prop_types(db))
    assert "rollup" in types, "dashboard_widgets 골든은 rollup 예시를 포함해야 합니다"
    assert "formula" in types, "dashboard_widgets 골든은 formula 예시를 포함해야 합니다"


# ── SKILL.md 계산속성 가이드 검증 (QUAL-2) ──

SKILLS_DIR = Path(__file__).resolve().parents[1].parent / "app" / "skills"


@pytest.mark.parametrize("skill", ["finance", "project", "crm", "sales"])
def test_premium_skills_document_calculated_properties(skill):
    """유료급 도메인 스킬은 rollup/formula 계산 속성을 SKILL.md에 명문화해야 한다."""
    fp = SKILLS_DIR / skill / "SKILL.md"
    assert fp.exists(), f"{skill}/SKILL.md 없음"
    text = fp.read_text(encoding="utf-8").lower()
    assert "formula" in text or "rollup" in text, (
        f"{skill}/SKILL.md는 계산 속성(formula/rollup) 가이드를 포함해야 합니다 (유료급 차별점)"
    )
