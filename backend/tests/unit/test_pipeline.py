"""Pipeline 테스트: 멀티 에이전트 파이프라인 단위 검증"""

from unittest.mock import AsyncMock, patch

import pytest

from app.agent.pipeline import (
    ARCHITECT_PROMPT,
    CONTENT_PROMPT,
    DESIGNER_PROMPT,
    VALIDATOR_PROMPT,
    multi_agent_pipeline,
)


class TestPromptConstants:
    def test_architect_prompt_exists(self):
        assert "ARCHITECT" in ARCHITECT_PROMPT
        assert "JSON" in ARCHITECT_PROMPT

    def test_designer_prompt_exists(self):
        assert "DESIGNER" in DESIGNER_PROMPT
        assert "color" in DESIGNER_PROMPT

    def test_content_prompt_exists(self):
        assert "CONTENT" in CONTENT_PROMPT
        assert "sample_items" in CONTENT_PROMPT

    def test_validator_prompt_exists(self):
        assert "VALIDATOR" in VALIDATOR_PROMPT


class TestMultiAgentPipeline:
    @pytest.fixture
    def mock_architecture(self):
        return {
            "title": "테스트",
            "databases": [{"title": "DB1", "properties": {"이름": "title"}}],
            "sub_pages": [],
        }

    async def test_architect_failure_yields_error(self):
        with patch("app.agent.pipeline._call_agent", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = None
            events = []
            async for event in multi_agent_pipeline("테스트"):
                events.append(event)
            assert any(e["stage"] == "error" for e in events)

    async def test_full_pipeline_success(self, mock_architecture):
        with patch("app.agent.pipeline._call_agent", new_callable=AsyncMock) as mock_call:
            mock_call.side_effect = [
                mock_architecture,
                {"color": "blue", "icon": "📋", "blocks": [{"type": "callout"}]},
                {"databases": [{"title": "DB1", "sample_items": [{"이름": "A"}]}]},
                mock_architecture,
            ]
            events = []
            async for event in multi_agent_pipeline("테스트"):
                events.append(event)
            stages = [e["stage"] for e in events]
            assert "architect" in stages
            assert "designer_done" in stages
            assert "content_done" in stages
            assert "complete" in stages

    async def test_designer_failure_continues(self, mock_architecture):
        with patch("app.agent.pipeline._call_agent", new_callable=AsyncMock) as mock_call:
            mock_call.side_effect = [
                mock_architecture,
                None,
                None,
                None,
            ]
            events = []
            async for event in multi_agent_pipeline("테스트"):
                events.append(event)
            assert any(e["stage"] == "complete" for e in events)

    async def test_validator_replaces_blueprint(self, mock_architecture):
        validated = {**mock_architecture, "databases": [{"title": "검증됨", "properties": {"이름": "title"}}]}
        with patch("app.agent.pipeline._call_agent", new_callable=AsyncMock) as mock_call:
            mock_call.side_effect = [
                mock_architecture,
                None,
                None,
                validated,
            ]
            events = []
            async for event in multi_agent_pipeline("테스트"):
                events.append(event)
            complete = [e for e in events if e["stage"] == "complete"]
            assert complete[0]["blueprint"]["databases"][0]["title"] == "검증됨"

    async def test_content_merges_sub_pages(self, mock_architecture):
        with patch("app.agent.pipeline._call_agent", new_callable=AsyncMock) as mock_call:
            mock_call.side_effect = [
                mock_architecture,
                None,
                {"sub_pages": [{"title": "새 페이지"}], "faq": [{"q": "Q1"}]},
                None,
            ]
            events = []
            async for event in multi_agent_pipeline("테스트"):
                events.append(event)
            assert any(e["stage"] == "complete" for e in events)
