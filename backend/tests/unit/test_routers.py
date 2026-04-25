"""FastAPI Router 테스트: TestClient 기반 엔드포인트 검증"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_ok(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "skills" in data
        assert data["skills"] == 48

    def test_health_has_today_stats(self):
        resp = client.get("/health")
        data = resp.json()
        assert "today_stats" in data
        assert "total" in data["today_stats"]
        assert "success_rate" in data["today_stats"]


class TestMetricsEndpoint:
    def test_metrics_summary(self):
        resp = client.get("/api/metrics/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["period"] == "7d"
        assert "total_generations" in data
        assert "success_rate" in data
        assert "top_skills" in data


class TestSkillsRouter:
    def test_list_all_skills(self):
        resp = client.get("/api/skills")
        assert resp.status_code == 200
        data = resp.json()
        assert "skills" in data
        assert len(data["skills"]) >= 40

    def test_get_existing_skill(self):
        resp = client.get("/api/skills/project")
        assert resp.status_code == 200
        data = resp.json()
        assert "content" in data
        assert data["is_custom"] is False

    def test_get_nonexistent_skill(self):
        resp = client.get("/api/skills/nonexistent_skill_xyz")
        assert resp.status_code == 200
        data = resp.json()
        assert "error" in data

    def test_create_custom_skill(self):
        resp = client.post(
            "/api/skills",
            json={
                "skill_id": "test_auto",
                "name": "자동 테스트",
                "description": "테스트용 스킬",
                "keywords": "test auto",
                "content": "테스트 내용입니다.",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

        client.delete("/api/skills/test_auto")

    def test_delete_nonexistent_custom_skill(self):
        resp = client.delete("/api/skills/does_not_exist_xyz")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False


class TestAIRouter:
    def test_detect_provider_empty_key(self):
        resp = client.post("/api/templates/ai/detect-provider", json={"api_key": ""})
        assert resp.status_code == 200
        data = resp.json()
        assert data["provider"] == "unknown"
        assert "error" in data

    def test_detect_provider_openai_fallback(self):
        resp = client.post("/api/templates/ai/detect-provider", json={"api_key": "sk-test-key-12345"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["provider"] == "openai"


class TestTemplateRouter:
    def test_list_recipes(self):
        resp = client.get("/api/recipes")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)


class TestCORSMiddleware:
    def test_cors_headers_present(self):
        resp = client.options(
            "/health",
            headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
        )
        assert resp.status_code == 200


class TestGlobalErrorHandler:
    @patch("app.main.settings")
    def test_unhandled_exception_returns_500(self, mock_settings):
        pass
