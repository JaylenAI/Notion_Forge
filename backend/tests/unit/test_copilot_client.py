"""CopilotManager 단위 테스트 — lifecycle, availability, send, status"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.copilot_client import COPILOT_MODELS, CopilotManager

# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def manager():
    """Fresh CopilotManager instance for each test"""
    return CopilotManager()


@pytest.fixture
def mock_copilot_module():
    """Mock the copilot SDK module"""
    mock_client_class = MagicMock()
    mock_client_instance = MagicMock()
    mock_client_instance.start = AsyncMock()
    mock_client_instance.stop = AsyncMock()
    mock_client_class.return_value = mock_client_instance

    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.data = MagicMock()
    mock_response.data.content = "Generated response text"
    mock_session.send_and_wait = AsyncMock(return_value=mock_response)
    mock_client_instance.create_session = AsyncMock(return_value=mock_session)

    return {
        "client_class": mock_client_class,
        "client_instance": mock_client_instance,
        "session": mock_session,
        "response": mock_response,
    }


# ============================================================
# Initialization Tests
# ============================================================


class TestCopilotManagerInit:
    def test_initial_state(self, manager):
        assert manager._client is None
        assert manager._available is None
        assert manager._started is False

    def test_get_models_returns_list(self, manager):
        models = manager.get_models()
        assert isinstance(models, list)
        assert len(models) == len(COPILOT_MODELS)
        for model in models:
            assert "id" in model
            assert "name" in model
            assert "provider" in model
            assert "tier" in model


# ============================================================
# Availability Tests
# ============================================================


class TestIsAvailable:
    def test_not_available_when_import_fails(self, manager):
        with patch("builtins.__import__", side_effect=ImportError("No module")):
            result = manager.is_available()
        assert result is False
        assert manager._available is False

    def test_available_when_import_succeeds(self, manager):
        with patch.dict("sys.modules", {"copilot": MagicMock()}):
            # Reset cached value
            manager._available = None
            result = manager.is_available()
        assert result is True

    def test_caches_result(self, manager):
        manager._available = True
        result = manager.is_available()
        assert result is True

    def test_caches_false_result(self, manager):
        manager._available = False
        result = manager.is_available()
        assert result is False


# ============================================================
# Lifecycle Tests (start/stop)
# ============================================================


class TestStart:
    async def test_start_when_not_available(self, manager):
        manager._available = False
        await manager.start()
        assert manager._started is False
        assert manager._client is None

    async def test_start_when_already_started(self, manager, mock_copilot_module):
        manager._available = True
        manager._started = True
        manager._client = mock_copilot_module["client_instance"]
        await manager.start()
        # Should not call start again
        mock_copilot_module["client_instance"].start.assert_not_called()

    async def test_start_success(self, manager, mock_copilot_module):
        manager._available = True
        with patch.dict(
            "sys.modules",
            {"copilot": MagicMock(CopilotClient=mock_copilot_module["client_class"])},
        ):
            await manager.start()
        assert manager._started is True
        assert manager._client is not None
        mock_copilot_module["client_instance"].start.assert_called_once()

    async def test_start_failure_sets_unavailable(self, manager):
        manager._available = True
        mock_client_class = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_instance.start = AsyncMock(side_effect=Exception("Connection failed"))
        mock_client_class.return_value = mock_client_instance

        with patch.dict(
            "sys.modules",
            {"copilot": MagicMock(CopilotClient=mock_client_class)},
        ):
            await manager.start()

        assert manager._started is False
        assert manager._client is None
        assert manager._available is False


class TestStop:
    async def test_stop_when_not_started(self, manager):
        await manager.stop()
        assert manager._started is False

    async def test_stop_success(self, manager, mock_copilot_module):
        manager._client = mock_copilot_module["client_instance"]
        manager._started = True
        await manager.stop()
        mock_copilot_module["client_instance"].stop.assert_called_once()
        assert manager._client is None
        assert manager._started is False

    async def test_stop_handles_exception(self, manager):
        mock_client = MagicMock()
        mock_client.stop = AsyncMock(side_effect=Exception("Cleanup error"))
        manager._client = mock_client
        manager._started = True
        await manager.stop()
        # Should not raise, and should still clean up
        assert manager._client is None
        assert manager._started is False


# ============================================================
# Send Tests
# ============================================================


class TestSend:
    async def test_send_returns_none_when_not_started(self, manager):
        result = await manager.send("system", "user message")
        assert result is None

    async def test_send_returns_none_when_no_client(self, manager):
        manager._started = True
        manager._client = None
        result = await manager.send("system", "user message")
        assert result is None

    async def test_send_success(self, manager, mock_copilot_module):
        manager._client = mock_copilot_module["client_instance"]
        manager._started = True

        mock_permission_handler = MagicMock()
        mock_permission_handler.approve_all = MagicMock()

        with patch.dict(
            "sys.modules",
            {
                "copilot": MagicMock(),
                "copilot.session": MagicMock(PermissionHandler=mock_permission_handler),
            },
        ):
            result = await manager.send("You are helpful", "Generate a plan")

        assert result == "Generated response text"
        mock_copilot_module["client_instance"].create_session.assert_called_once()
        mock_copilot_module["session"].send_and_wait.assert_called_once()

    async def test_send_with_custom_model(self, manager, mock_copilot_module):
        manager._client = mock_copilot_module["client_instance"]
        manager._started = True

        mock_permission_handler = MagicMock()
        mock_permission_handler.approve_all = MagicMock()

        with patch.dict(
            "sys.modules",
            {
                "copilot": MagicMock(),
                "copilot.session": MagicMock(PermissionHandler=mock_permission_handler),
            },
        ):
            await manager.send("system", "msg", model="gpt-5.2")

        create_kwargs = mock_copilot_module["client_instance"].create_session.call_args[1]
        assert create_kwargs["model"] == "gpt-5.2"

    async def test_send_returns_none_on_timeout(self, manager, mock_copilot_module):
        manager._client = mock_copilot_module["client_instance"]
        manager._started = True
        mock_copilot_module["session"].send_and_wait = AsyncMock(side_effect=TimeoutError("Timeout"))

        mock_permission_handler = MagicMock()
        mock_permission_handler.approve_all = MagicMock()

        with patch.dict(
            "sys.modules",
            {
                "copilot": MagicMock(),
                "copilot.session": MagicMock(PermissionHandler=mock_permission_handler),
            },
        ):
            result = await manager.send("system", "msg", timeout=5.0)

        assert result is None

    async def test_send_returns_none_on_exception(self, manager, mock_copilot_module):
        manager._client = mock_copilot_module["client_instance"]
        manager._started = True
        mock_copilot_module["client_instance"].create_session = AsyncMock(side_effect=Exception("Network error"))

        mock_permission_handler = MagicMock()
        mock_permission_handler.approve_all = MagicMock()

        with patch.dict(
            "sys.modules",
            {
                "copilot": MagicMock(),
                "copilot.session": MagicMock(PermissionHandler=mock_permission_handler),
            },
        ):
            result = await manager.send("system", "msg")

        assert result is None

    async def test_send_returns_none_when_response_empty(self, manager, mock_copilot_module):
        manager._client = mock_copilot_module["client_instance"]
        manager._started = True
        mock_copilot_module["session"].send_and_wait = AsyncMock(return_value=None)

        mock_permission_handler = MagicMock()
        mock_permission_handler.approve_all = MagicMock()

        with patch.dict(
            "sys.modules",
            {
                "copilot": MagicMock(),
                "copilot.session": MagicMock(PermissionHandler=mock_permission_handler),
            },
        ):
            result = await manager.send("system", "msg")

        assert result is None

    async def test_send_returns_none_when_response_data_none(self, manager, mock_copilot_module):
        manager._client = mock_copilot_module["client_instance"]
        manager._started = True
        mock_response = MagicMock()
        mock_response.data = None
        mock_copilot_module["session"].send_and_wait = AsyncMock(return_value=mock_response)

        mock_permission_handler = MagicMock()
        mock_permission_handler.approve_all = MagicMock()

        with patch.dict(
            "sys.modules",
            {
                "copilot": MagicMock(),
                "copilot.session": MagicMock(PermissionHandler=mock_permission_handler),
            },
        ):
            result = await manager.send("system", "msg")

        assert result is None


# ============================================================
# GetStatus Tests
# ============================================================


class TestGetStatus:
    def test_status_when_not_available(self, manager):
        manager._available = False
        with patch("app.config.settings", MagicMock(copilot_model="gpt-4.1")):
            status = manager.get_status()
        assert status["available"] is False
        assert status["started"] is False
        assert status["models"] == []

    def test_status_when_started(self, manager):
        manager._available = True
        manager._started = True
        with patch("app.config.settings", MagicMock(copilot_model="gpt-5.2")):
            status = manager.get_status()
        assert status["available"] is True
        assert status["started"] is True
        assert status["current_model"] == "gpt-5.2"
        assert len(status["models"]) == len(COPILOT_MODELS)


# ============================================================
# Module-Level Singleton Test
# ============================================================


class TestSingleton:
    def test_copilot_manager_is_singleton(self):
        from app.core.copilot_client import copilot_manager

        assert isinstance(copilot_manager, CopilotManager)
