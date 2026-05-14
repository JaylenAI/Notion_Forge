"""Worker scaffold 생성 + 배포 도구"""

from typing import Any

from app.agent.tools.base import BaseTool
from app.notion.client import NotionClient
from app.notion.worker_builder import (
    build_sync_worker,
    build_tool_worker,
    build_webhook_worker,
    build_worker_project,
)


class CreateWorkerTool(BaseTool):
    name = "create_worker"
    description = "Notion Worker를 생성합니다 (sync: 외부 데이터 동기화, tool: 커스텀 액션, webhook: 이벤트 자동화)"
    parameters = {
        "name": {"type": "string", "description": "Worker 이름"},
        "worker_type": {
            "type": "string",
            "description": "Worker 타입 (sync, tool, webhook)",
        },
        "description": {"type": "string", "description": "Worker 설명", "optional": True},
        "database_id": {"type": "string", "description": "대상 DB ID (sync/webhook)", "optional": True},
        "event_type": {
            "type": "string",
            "description": "이벤트 타입 (webhook만 — page.created, page.updated 등)",
            "optional": True,
        },
        "properties": {
            "type": "object",
            "description": "DB 속성 매핑 (sync만 — {Name: title, Status: select})",
            "optional": True,
        },
        "parameters": {
            "type": "object",
            "description": "Tool 파라미터 (tool만 — {query: {type: string, description: ...}})",
            "optional": True,
        },
        "deploy": {
            "type": "boolean",
            "description": "생성 후 즉시 배포할지 여부",
            "optional": True,
        },
    }

    def __init__(self, client: NotionClient):
        self.client = client

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        name = kwargs["name"]
        worker_type = kwargs["worker_type"]
        description = kwargs.get("description", "")

        if worker_type == "sync":
            worker = build_sync_worker(
                name=name,
                source_description=description,
                properties=kwargs.get("properties"),
            )
        elif worker_type == "tool":
            worker = build_tool_worker(
                name=name,
                description=description,
                parameters=kwargs.get("parameters"),
            )
        elif worker_type == "webhook":
            worker = build_webhook_worker(
                name=name,
                event_type=kwargs.get("event_type", "page.created"),
                database_id=kwargs.get("database_id", ""),
            )
        else:
            return {"error": f"지원하지 않는 Worker 타입: {worker_type}"}

        project = build_worker_project([worker], project_name=f"notionforge-{name.lower().replace(' ', '-')}")

        result: dict[str, Any] = {
            "worker_type": worker_type,
            "name": name,
            "project": project,
            "files_count": len(project["files"]),
        }

        if kwargs.get("deploy"):
            deploy_result = await self.client.deploy_worker(
                title=name,
                worker_type=worker_type,
                code=worker["code"],
                database_id=kwargs.get("database_id", ""),
                description=description,
            )
            result["deploy"] = deploy_result

        return result
