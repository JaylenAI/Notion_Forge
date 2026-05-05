"""스킬 라우터 CRUD 테스트"""

from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


class TestSkillsList:
    async def test_list_skills(self, client):
        resp = await client.get("/api/skills")
        assert resp.status_code == 200
        data = resp.json()
        assert "skills" in data
        assert len(data["skills"]) > 0


class TestSkillDetail:
    async def test_get_builtin_skill(self, client):
        with patch("app.routers.skills.get_custom_skill", return_value=None):
            with patch("app.routers.skills.load_skill", return_value="# Skill Content"):
                resp = await client.get("/api/skills/project_management")
                assert resp.status_code == 200
                data = resp.json()
                assert data["is_custom"] is False

    async def test_get_custom_skill(self, client):
        custom_data = {"id": "my-skill", "content": "# My Skill"}
        with patch("app.routers.skills.get_custom_skill", return_value=custom_data):
            resp = await client.get("/api/skills/my-skill")
            assert resp.status_code == 200
            data = resp.json()
            assert data["is_custom"] is True

    async def test_skill_not_found(self, client):
        with patch("app.routers.skills.get_custom_skill", return_value=None):
            with patch("app.routers.skills.load_skill", return_value=None):
                resp = await client.get("/api/skills/nonexistent")
                data = resp.json()
                assert "error" in data


class TestSkillCRUD:
    async def test_create_custom_skill(self, client):
        with patch("app.routers.skills.save_custom_skill") as mock_save:
            resp = await client.post(
                "/api/skills",
                json={
                    "skill_id": "meeting",
                    "name": "Meeting Notes",
                    "description": "회의록 생성",
                    "keywords": "회의,미팅",
                    "content": "회의록 템플릿",
                },
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["success"] is True
            assert mock_save.called

    async def test_create_skill_with_frontmatter(self, client):
        with patch("app.routers.skills.save_custom_skill") as mock_save:
            resp = await client.post(
                "/api/skills",
                json={
                    "skill_id": "custom",
                    "name": "Custom",
                    "description": "test",
                    "content": "---\nname: custom\n---\n# Body",
                },
            )
            assert resp.status_code == 200
            saved_content = mock_save.call_args[0][1]
            assert saved_content.startswith("---")

    async def test_update_custom_skill(self, client):
        with patch("app.routers.skills.save_custom_skill") as mock_save:
            resp = await client.put(
                "/api/skills/meeting",
                json={
                    "skill_id": "meeting",
                    "name": "Meeting v2",
                    "description": "업데이트",
                    "content": "새 내용",
                },
            )
            assert resp.status_code == 200
            assert mock_save.called

    async def test_delete_existing_skill(self, client):
        with patch("app.routers.skills.delete_custom_skill", return_value=True):
            resp = await client.delete("/api/skills/my-skill")
            assert resp.status_code == 200
            data = resp.json()
            assert data["success"] is True

    async def test_delete_nonexistent_skill(self, client):
        with patch("app.routers.skills.delete_custom_skill", return_value=False):
            resp = await client.delete("/api/skills/nope")
            data = resp.json()
            assert data["success"] is False
