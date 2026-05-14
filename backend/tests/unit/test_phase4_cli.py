"""Phase 4 Notion CLI 래퍼 + 오픈소스 준비 테스트"""

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.notion.cli import NotionCLI

# ============================================================
# NotionCLI 테스트
# ============================================================


class TestNotionCLIAvailability:
    def test_available_when_ntn_found(self):
        with patch("shutil.which", return_value="/usr/local/bin/ntn"):
            cli = NotionCLI()
            assert cli.available is True

    def test_not_available_when_ntn_missing(self):
        with patch("shutil.which", return_value=None):
            cli = NotionCLI()
            assert cli.available is False


class TestNotionCLIRun:
    @pytest.mark.asyncio
    async def test_run_not_available(self):
        with patch("shutil.which", return_value=None):
            cli = NotionCLI()
            result = await cli.run("whoami")
            assert "error" in result
            assert "설치되지 않았습니다" in result["error"]

    @pytest.mark.asyncio
    async def test_run_success_json(self):
        with patch("shutil.which", return_value="/usr/local/bin/ntn"):
            cli = NotionCLI()

            mock_proc = AsyncMock()
            mock_proc.returncode = 0
            mock_proc.communicate = AsyncMock(
                return_value=(
                    json.dumps({"user": "test@example.com"}).encode(),
                    b"",
                )
            )

            with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
                result = await cli.run("whoami")
                assert result["exit_code"] == 0
                assert result["data"]["user"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_run_success_text(self):
        with patch("shutil.which", return_value="/usr/local/bin/ntn"):
            cli = NotionCLI()

            mock_proc = AsyncMock()
            mock_proc.returncode = 0
            mock_proc.communicate = AsyncMock(return_value=(b"ntn v1.2.3", b""))

            with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
                result = await cli.run("--version")
                assert result["exit_code"] == 0
                assert result["output"] == "ntn v1.2.3"

    @pytest.mark.asyncio
    async def test_run_error(self):
        with patch("shutil.which", return_value="/usr/local/bin/ntn"):
            cli = NotionCLI()

            mock_proc = AsyncMock()
            mock_proc.returncode = 1
            mock_proc.communicate = AsyncMock(return_value=(b"", b"Error: unauthorized"))

            with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
                result = await cli.run("deploy")
                assert result["exit_code"] == 1
                assert "unauthorized" in result["error"]

    @pytest.mark.asyncio
    async def test_run_with_token(self):
        with patch("shutil.which", return_value="/usr/local/bin/ntn"):
            cli = NotionCLI(token="ntn_test_token")

            mock_proc = AsyncMock()
            mock_proc.returncode = 0
            mock_proc.communicate = AsyncMock(return_value=(b"{}", b""))

            with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
                await cli.run("whoami")
                call_args = mock_exec.call_args[0]
                assert "--token" in call_args
                assert "ntn_test_token" in call_args


class TestNotionCLIMethods:
    @pytest.mark.asyncio
    async def test_api_get(self):
        with patch("shutil.which", return_value="/usr/local/bin/ntn"):
            cli = NotionCLI()

            mock_proc = AsyncMock()
            mock_proc.returncode = 0
            mock_proc.communicate = AsyncMock(return_value=(json.dumps({"results": []}).encode(), b""))

            with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
                await cli.api("get", "/users")
                call_args = mock_exec.call_args[0]
                assert "api" in call_args
                assert "GET" in call_args
                assert "/users" in call_args

    @pytest.mark.asyncio
    async def test_api_post_with_body(self):
        with patch("shutil.which", return_value="/usr/local/bin/ntn"):
            cli = NotionCLI()

            mock_proc = AsyncMock()
            mock_proc.returncode = 0
            mock_proc.communicate = AsyncMock(return_value=(b'{"id":"page-1"}', b""))

            with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
                body = {"parent": {"page_id": "abc"}, "properties": {}}
                await cli.api("post", "/pages", body=body)
                call_args = mock_exec.call_args[0]
                assert "--body" in call_args

    @pytest.mark.asyncio
    async def test_deploy(self):
        with patch("shutil.which", return_value="/usr/local/bin/ntn"):
            cli = NotionCLI()

            mock_proc = AsyncMock()
            mock_proc.returncode = 0
            mock_proc.communicate = AsyncMock(return_value=(b'{"status":"deployed"}', b""))

            with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
                await cli.deploy("/path/to/project")
                call_args = mock_exec.call_args[0]
                assert "deploy" in call_args
                assert "--dir" in call_args

    @pytest.mark.asyncio
    async def test_logs(self):
        with patch("shutil.which", return_value="/usr/local/bin/ntn"):
            cli = NotionCLI()

            mock_proc = AsyncMock()
            mock_proc.returncode = 0
            mock_proc.communicate = AsyncMock(return_value=(b'{"results":[]}', b""))

            with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
                await cli.logs("worker-123", limit=10)
                call_args = mock_exec.call_args[0]
                assert "logs" in call_args
                assert "worker-123" in call_args
                assert "10" in call_args

    @pytest.mark.asyncio
    async def test_whoami(self):
        with patch("shutil.which", return_value="/usr/local/bin/ntn"):
            cli = NotionCLI()

            mock_proc = AsyncMock()
            mock_proc.returncode = 0
            mock_proc.communicate = AsyncMock(return_value=(json.dumps({"workspace": "My Workspace"}).encode(), b""))

            with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
                result = await cli.whoami()
                assert result["data"]["workspace"] == "My Workspace"

    @pytest.mark.asyncio
    async def test_version(self):
        with patch("shutil.which", return_value="/usr/local/bin/ntn"):
            cli = NotionCLI()

            mock_proc = AsyncMock()
            mock_proc.returncode = 0
            mock_proc.communicate = AsyncMock(return_value=(b"ntn v2.0.0", b""))

            with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
                result = await cli.version()
                assert "ntn v2.0.0" in result["output"]
