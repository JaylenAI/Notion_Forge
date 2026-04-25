"""WebSocket 채팅 라우터

핵심 구조: agent.process()를 별도 태스크로 실행하여
Approval Gate 대기 중에도 WebSocket 메시지(confirm_create 등)를 수신할 수 있도록 함.
"""

import asyncio
import json
import logging
import traceback

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("notionforge.chat")

from app.agent.orchestrator import AgentOrchestrator

router = APIRouter(tags=["chat"])


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    agent: AgentOrchestrator | None = None
    process_task: asyncio.Task | None = None

    def _handle_control_message(msg_type: str, data: dict) -> bool:
        """설정/승인 등 제어 메시지 처리. 처리했으면 True 반환."""
        nonlocal agent

        if msg_type == "confirm_create" and agent:
            agent.approve_creation(approved=True)
            return True

        if msg_type == "cancel_create" and agent:
            agent.approve_creation(approved=False)
            return True

        if msg_type == "cancel":
            return True

        if msg_type == "set_complexity" and agent:
            agent.complexity = data.get("complexity", "standard")
            asyncio.create_task(websocket.send_json({"type": "system", "content": f"복잡도 설정: {agent.complexity}"}))
            return True

        if msg_type == "set_language" and agent:
            agent.language = data.get("language", "ko")
            asyncio.create_task(websocket.send_json({"type": "system", "content": f"언어 설정: {agent.language}"}))
            return True

        if msg_type == "set_pipeline" and agent:
            agent.use_pipeline = data.get("enabled", False)
            mode = "Multi-Agent Pipeline" if agent.use_pipeline else "Single Agent"
            asyncio.create_task(websocket.send_json({"type": "system", "content": f"AI 모드: {mode}"}))
            return True

        return False

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)

            msg_type = data.get("type", "message")
            content = data.get("content", "")

            # ── init: 에이전트 초기화 ──
            if msg_type == "init":
                agent = AgentOrchestrator(
                    notion_token=data.get("notion_token", ""),
                    parent_page_id=data.get("parent_page_id", ""),
                    ai_key=data.get("ai_key", ""),
                    ai_model=data.get("ai_model", ""),
                )
                await websocket.send_json({"type": "system", "content": "연결 완료! 어떤 템플릿을 만들어드릴까요?"})
                continue

            # ── 제어 메시지 (승인/취소/설정) ──
            if _handle_control_message(msg_type, data):
                continue

            # ── 사용자 메시지 → agent.process() 실행 ──
            if agent is None:
                agent = AgentOrchestrator()

            # 이전 태스크가 아직 돌고 있으면 완료 대기
            if process_task and not process_task.done():
                continue

            async def _run_process(a: AgentOrchestrator, msg: str):
                """agent.process()를 별도 태스크로 실행하여 이벤트를 WebSocket에 전송"""
                try:
                    async for event in a.process(msg):
                        try:
                            await websocket.send_json(event)
                        except Exception:
                            break
                except Exception as e:
                    tb = traceback.format_exc()
                    logger.error(f"[Agent 에러]\n{tb}")
                    try:
                        await websocket.send_json({"type": "error", "content": f"처리 중 오류: {str(e)[:200]}"})
                    except Exception:
                        pass

            process_task = asyncio.create_task(_run_process(agent, content))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"[WebSocket 에러] {e}")
        try:
            await websocket.send_json({"type": "error", "content": str(e)[:200]})
        except Exception:
            pass
    finally:
        if process_task and not process_task.done():
            process_task.cancel()
