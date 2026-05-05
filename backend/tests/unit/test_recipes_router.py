"""레시피 갤러리 라우터 테스트"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture
def mock_recipes_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        recipes_dir = Path(tmpdir)

        recipe1 = {
            "id": "project-board",
            "name": "프로젝트 보드",
            "name_en": "Project Board",
            "description": "태스크 관리",
            "category": "productivity",
            "icon": "📊",
            "author": "NotionForge",
            "tags": ["project", "kanban"],
            "complexity": "standard",
            "blueprint": {"main_page": {"title": "프로젝트"}},
        }
        recipe2 = {
            "id": "reading-log",
            "name": "독서 기록",
            "description": "읽은 책 기록",
            "category": "personal",
            "icon": "📚",
            "tags": ["book", "reading"],
        }

        (recipes_dir / "project-board.json").write_text(json.dumps(recipe1, ensure_ascii=False))
        (recipes_dir / "reading-log.json").write_text(json.dumps(recipe2, ensure_ascii=False))

        with patch("app.routers.recipes.RECIPES_DIR", recipes_dir):
            yield recipes_dir


class TestListRecipes:
    async def test_list_all(self, client, mock_recipes_dir):
        resp = await client.get("/api/recipes")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert len(data["recipes"]) == 2

    async def test_filter_by_category(self, client, mock_recipes_dir):
        resp = await client.get("/api/recipes?category=productivity")
        data = resp.json()
        assert data["total"] == 1
        assert data["recipes"][0]["id"] == "project-board"

    async def test_search(self, client, mock_recipes_dir):
        resp = await client.get("/api/recipes?search=독서")
        data = resp.json()
        assert data["total"] == 1
        assert data["recipes"][0]["id"] == "reading-log"

    async def test_search_by_tag(self, client, mock_recipes_dir):
        resp = await client.get("/api/recipes?search=kanban")
        data = resp.json()
        assert data["total"] == 1

    async def test_empty_results(self, client, mock_recipes_dir):
        resp = await client.get("/api/recipes?category=nonexistent")
        data = resp.json()
        assert data["total"] == 0


class TestGetRecipe:
    async def test_get_existing(self, client, mock_recipes_dir):
        resp = await client.get("/api/recipes/project-board")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "project-board"
        assert "blueprint" in data

    async def test_get_nonexistent(self, client, mock_recipes_dir):
        resp = await client.get("/api/recipes/nope")
        assert resp.status_code == 404

    async def test_invalid_id(self, client, mock_recipes_dir):
        resp = await client.get("/api/recipes/invalid!@#$%id")
        assert resp.status_code == 400


class TestCategories:
    async def test_list_categories(self, client, mock_recipes_dir):
        resp = await client.get("/api/recipes/categories/list")
        assert resp.status_code == 200
        data = resp.json()
        assert "personal" in data["categories"]
        assert "productivity" in data["categories"]
