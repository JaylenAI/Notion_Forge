"""WebSocket 채팅 라우터"""

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.agent.orchestrator import AgentOrchestrator

router = APIRouter(tags=["chat"])


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    agent: AgentOrchestrator | None = None

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)

            msg_type = data.get("type", "message")
            content = data.get("content", "")

            if msg_type == "init":
                agent = AgentOrchestrator(
                    notion_token=data.get("notion_token", ""),
                    parent_page_id=data.get("parent_page_id", ""),
                    ai_key=data.get("ai_key", ""),
                    ai_model=data.get("ai_model", ""),
                )
                await websocket.send_json({"type": "system", "content": "연결 완료! 어떤 템플릿을 만들어드릴까요?"})
                continue

            if agent is None:
                agent = AgentOrchestrator()

            async for event in agent.process(content):
                await websocket.send_json(event)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "content": str(e)})
        except Exception:
            pass
