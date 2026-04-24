"""커뮤니티 레시피 갤러리 API"""

import json
import logging
import re
from pathlib import Path

from fastapi import APIRouter, HTTPException

logger = logging.getLogger("notionforge.recipes")

router = APIRouter(prefix="/api/recipes", tags=["recipes"])

_SAFE_RECIPE_ID = re.compile(r"^[a-zA-Z0-9_-]{1,100}$")

RECIPES_DIR = Path(__file__).resolve().parents[3] / "recipes"


def _load_recipes() -> list[dict]:
    """recipes/ 디렉토리에서 모든 레시피 JSON 로드"""
    recipes = []
    if not RECIPES_DIR.exists():
        return recipes
    for fp in sorted(RECIPES_DIR.glob("*.json")):
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
            # 목록용: blueprint는 제외 (크기 절약)
            recipes.append({
                "id": data.get("id", fp.stem),
                "name": data.get("name", fp.stem),
                "name_en": data.get("name_en", ""),
                "description": data.get("description", ""),
                "description_en": data.get("description_en", ""),
                "category": data.get("category", "general"),
                "icon": data.get("icon", "📋"),
                "author": data.get("author", "Community"),
                "tags": data.get("tags", []),
                "complexity": data.get("complexity", "standard"),
            })
        except Exception as e:
            logger.warning(f"[Recipe 로드 실패] {fp.name}: {e}")
    return recipes


@router.get("")
async def list_recipes(category: str = "", search: str = ""):
    """레시피 목록 조회 (카테고리 필터, 검색)"""
    recipes = _load_recipes()

    if category:
        recipes = [r for r in recipes if r["category"] == category]

    if search:
        q = search.lower()
        recipes = [
            r for r in recipes
            if q in r["name"].lower() or q in r.get("description", "").lower()
            or any(q in tag for tag in r.get("tags", []))
        ]

    return {"recipes": recipes, "total": len(recipes)}


@router.get("/{recipe_id}")
async def get_recipe(recipe_id: str):
    """레시피 상세 조회 (blueprint 포함)"""
    if not _SAFE_RECIPE_ID.match(recipe_id):
        raise HTTPException(status_code=400, detail="잘못된 레시피 ID 형식입니다.")
    fp = RECIPES_DIR / f"{recipe_id}.json"
    if fp.resolve().parent != RECIPES_DIR.resolve():
        raise HTTPException(status_code=400, detail="잘못된 경로입니다.")
    if not fp.exists():
        raise HTTPException(status_code=404, detail="레시피를 찾을 수 없습니다.")
    try:
        data = json.loads(fp.read_text(encoding="utf-8"))
        return data
    except Exception:
        raise HTTPException(status_code=500, detail="레시피 로드 실패")


@router.get("/categories/list")
async def list_categories():
    """레시피 카테고리 목록"""
    recipes = _load_recipes()
    categories = sorted(set(r["category"] for r in recipes))
    return {"categories": categories}
