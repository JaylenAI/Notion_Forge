"""Notion CLI (ntn) 래퍼 — Python에서 ntn 명령 실행

Notion CLI 주요 명령:
- ntn api <method> <path> [--body=json] : REST API 호출
- ntn deploy : Worker 배포
- ntn dev : 로컬 Worker 개발 서버
- ntn logs <worker-id> : Worker 로그 조회
- ntn login : 인증
- ntn whoami : 현재 인증 정보 확인
"""

import asyncio
import json
import logging
import shutil
from typing import Any

logger = logging.getLogger("notionforge.cli")


class NotionCLI:
    def __init__(self, token: str = ""):
        self._token = token
        self._ntn_path = shutil.which("ntn")

    @property
    def available(self) -> bool:
        return self._ntn_path is not None

    async def run(self, *args: str, timeout: float = 30.0) -> dict[str, Any]:
        if not self.available:
            return {"error": "ntn CLI가 설치되지 않았습니다. npm install -g @notionhq/ntn"}

        env_args: list[str] = []
        if self._token:
            env_args = ["--token", self._token]

        cmd = [self._ntn_path, *args, *env_args]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)

            output = stdout.decode("utf-8").strip()
            error_output = stderr.decode("utf-8").strip()

            if proc.returncode != 0:
                logger.warning(f"[ntn 에러] exit={proc.returncode} stderr={error_output[:200]}")
                return {
                    "exit_code": proc.returncode,
                    "error": error_output[:500],
                    "stdout": output[:500],
                }

            try:
                data = json.loads(output)
                return {"exit_code": 0, "data": data}
            except json.JSONDecodeError:
                return {"exit_code": 0, "output": output}

        except asyncio.TimeoutError:
            return {"error": f"ntn 명령 타임아웃 ({timeout}s)"}
        except Exception as e:
            return {"error": f"ntn 실행 실패: {str(e)[:200]}"}

    async def api(self, method: str, path: str, body: dict | None = None) -> dict[str, Any]:
        args = ["api", method.upper(), path]
        if body:
            args.extend(["--body", json.dumps(body)])
        return await self.run(*args)

    async def deploy(self, project_dir: str = ".") -> dict[str, Any]:
        return await self.run("deploy", "--dir", project_dir, timeout=120.0)

    async def dev(self, project_dir: str = ".") -> dict[str, Any]:
        return await self.run("dev", "--dir", project_dir, timeout=10.0)

    async def logs(self, worker_id: str, limit: int = 50) -> dict[str, Any]:
        return await self.run("logs", worker_id, "--limit", str(limit))

    async def whoami(self) -> dict[str, Any]:
        return await self.run("whoami")

    async def version(self) -> dict[str, Any]:
        return await self.run("--version")
