"""WebSocket 채팅 라우터"""

import json
import traceback

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

            # 복잡도 설정
            if msg_type == "set_complexity" and agent:
                agent.complexity = data.get("complexity", "standard")
                await websocket.send_json({"type": "system", "content": f"복잡도 설정: {agent.complexity}"})
                continue

            # 언어 설정
            if msg_type == "set_language" and agent:
                agent.language = data.get("language", "ko")
                await websocket.send_json({"type": "system", "content": f"언어 설정: {agent.language}"})
                continue

            # 파이프라인 모드 설정
            if msg_type == "set_pipeline" and agent:
                agent.use_pipeline = data.get("enabled", False)
                mode = "Multi-Agent Pipeline" if agent.use_pipeline else "Single Agent"
                await websocket.send_json({"type": "system", "content": f"AI 모드: {mode}"})
                continue

            if msg_type == "cancel":
                continue

            if agent is None:
                agent = AgentOrchestrator()

            try:
                async for event in agent.process(content):
                    try:
                        await websocket.send_json(event)
                    except Exception:
                        break
            except Exception as e:
                tb = traceback.format_exc()
                print(f"[Agent 에러]\n{tb}")
                try:
                    await websocket.send_json({
                        "type": "error",
                        "content": f"메인 페이지 생성 실패: {str(e)[:200]}"
                    })
                except Exception:
                    pass

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[WebSocket 에러] {e}")
        try:
            await websocket.send_json({"type": "error", "content": str(e)[:200]})
        except Exception:
            pass
