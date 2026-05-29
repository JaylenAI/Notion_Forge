"""비동기 작업 관리 라우터 — Background Task + Polling 패턴

복잡한 템플릿 생성이 120초를 초과할 수 있으므로,
작업을 백그라운드로 실행하고 상태를 폴링하는 패턴 제공.
"""

import asyncio
import logging
import time
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agent.orchestrator import AgentOrchestrator
from app.core.middleware import sanitize_error

logger = logging.getLogger("notionforge.tasks")

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


class TaskSubmitRequest(BaseModel):
    prompt: str = Field(min_length=2, max_length=2000)
    notion_token: str = Field(min_length=1, max_length=200)
    parent_page_id: str = Field(min_length=1, max_length=50, pattern=r"^[a-f0-9-]+$")
    options: dict | None = None


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: list[dict[str, Any]] = []
    result: dict[str, Any] | None = None
    error: str | None = None
    created_at: float
    completed_at: float | None = None


_task_store: dict[str, dict[str, Any]] = {}

MAX_TASK_AGE = 3600
MAX_CONCURRENT_TASKS = 10


def _cleanup_old_tasks() -> None:
    now = time.time()
    expired = [tid for tid, t in _task_store.items() if now - t["created_at"] > MAX_TASK_AGE]
    for tid in expired:
        del _task_store[tid]


async def _run_generation(task_id: str, prompt: str, notion_token: str, parent_page_id: str) -> None:
    task = _task_store[task_id]
    task["status"] = "running"

    try:
        agent = AgentOrchestrator(
            notion_token=notion_token,
            parent_page_id=parent_page_id,
        )

        async for event in agent.process(prompt):
            event_type = event.get("type", "")

            if event_type == "approval_request":
                agent.approve_creation(approved=True)
            elif event_type == "progress":
                task["progress"].append(
                    {
                        "step": event.get("step", ""),
                        "message": event.get("message", ""),
                        "timestamp": time.time(),
                    }
                )
            elif event_type == "complete":
                result = event.get("result", {})
                task["status"] = "completed"
                task["result"] = {
                    "success": True,
                    "notion_url": result.get("main_url"),
                    "page_id": result["pages"][0]["id"] if result.get("pages") else None,
                    "summary": {
                        "pages": len(result.get("pages", [])),
                        "databases": len(result.get("databases", [])),
                        "blocks": result.get("blocks", 0),
                    },
                }
                task["completed_at"] = time.time()
                return
            elif event_type == "error":
                task["status"] = "failed"
                task["error"] = event.get("content", "알 수 없는 오류")
                task["completed_at"] = time.time()
                return
            elif event_type == "question":
                task["status"] = "failed"
                task["error"] = f"추가 정보 필요: {event.get('content', '')}"
                task["completed_at"] = time.time()
                return

        if task["status"] == "running":
            task["status"] = "failed"
            task["error"] = "생성 완료 이벤트를 받지 못했습니다"
            task["completed_at"] = time.time()

    except Exception as e:
        logger.error(f"[Task {task_id}] 생성 실패: {e}", exc_info=True)
        task["status"] = "failed"
        task["error"] = sanitize_error(e)
        task["completed_at"] = time.time()


@router.post("/submit", response_model=TaskStatusResponse)
async def submit_task(req: TaskSubmitRequest):
    """템플릿 생성 작업을 백그라운드로 제출"""
    _cleanup_old_tasks()

    running_count = sum(1 for t in _task_store.values() if t["status"] == "running")
    if running_count >= MAX_CONCURRENT_TASKS:
        raise HTTPException(status_code=429, detail="동시 작업 수 한도 초과. 잠시 후 다시 시도해주세요.")

    task_id = str(uuid.uuid4())[:12]
    now = time.time()

    _task_store[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "progress": [],
        "result": None,
        "error": None,
        "created_at": now,
        "completed_at": None,
    }

    asyncio.create_task(_run_generation(task_id, req.prompt, req.notion_token, req.parent_page_id))

    return TaskStatusResponse(**_task_store[task_id])


@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """작업 상태 조회 (폴링)"""
    _cleanup_old_tasks()  # 조회 시에도 만료 task 정리 (저트래픽 시 누수 방지)
    if task_id not in _task_store:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")

    return TaskStatusResponse(**_task_store[task_id])


@router.delete("/{task_id}")
async def cancel_task(task_id: str):
    """작업 취소/삭제"""
    if task_id not in _task_store:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")

    task = _task_store[task_id]
    if task["status"] == "running":
        task["status"] = "cancelled"
        task["completed_at"] = time.time()

    del _task_store[task_id]
    return {"success": True, "message": "작업이 삭제되었습니다"}
