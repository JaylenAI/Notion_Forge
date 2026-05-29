"""WebSocket 채팅 라우터

핵심 구조: agent.process()를 별도 태스크로 실행하여
Approval Gate 대기 중에도 WebSocket 메시지(confirm_create 등)를 수신할 수 있도록 함.
"""

import asyncio
import json
import logging
from collections import defaultdict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("notionforge.chat")

from app.agent.orchestrator import AgentOrchestrator
from app.core.middleware import sanitize_error

router = APIRouter(tags=["chat"])


WS_INIT_TIMEOUT = 10
WS_MESSAGE_RATE_LIMIT = 20

# WebSocket 연결 단위 DoS 방어 (HTTP RateLimitMiddleware는 WS 핸드셰이크를 못 막음)
WS_MAX_CONN_PER_IP = 5  # IP당 동시 연결 수
WS_MAX_NEW_PER_MIN = 30  # IP당 분당 신규 연결 수
_ws_active: dict[str, int] = defaultdict(int)
_ws_recent_connects: dict[str, list[float]] = defaultdict(list)


def _ws_client_ip(websocket: WebSocket) -> str:
    fwd = websocket.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return websocket.client.host if websocket.client else "unknown"


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    # ── 연결 단위 IP rate limit (accept 전 검사) ──
    ip = _ws_client_ip(websocket)
    _now = asyncio.get_event_loop().time()
    recent = [t for t in _ws_recent_connects[ip] if _now - t < 60]
    if _ws_active[ip] >= WS_MAX_CONN_PER_IP or len(recent) >= WS_MAX_NEW_PER_MIN:
        await websocket.accept()
        await websocket.send_json({"type": "error", "content": "연결 한도 초과. 잠시 후 다시 시도해주세요."})
        await websocket.close(code=4029)
        return
    recent.append(_now)
    _ws_recent_connects[ip] = recent
    _ws_active[ip] += 1

    await websocket.accept()

    agent: AgentOrchestrator | None = None
    process_task: asyncio.Task | None = None
    message_timestamps: list[float] = []

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

        if msg_type == "set_agent_loop" and agent:
            agent.use_agent_loop = data.get("enabled", False)
            mode = "Agent Loop (Plan-Execute-Reflect)" if agent.use_agent_loop else "표준 파이프라인"
            asyncio.create_task(websocket.send_json({"type": "system", "content": f"생성 모드: {mode}"}))
            return True

        return False

    try:
        # init 메시지 대기 (타임아웃 적용)
        try:
            raw = await asyncio.wait_for(websocket.receive_text(), timeout=WS_INIT_TIMEOUT)
            init_data = json.loads(raw)
            if init_data.get("type") != "init":
                await websocket.send_json({"type": "error", "content": "init 메시지가 필요합니다."})
                await websocket.close(code=4001)
                return
            from app.config import settings

            notion_token = init_data.get("notion_token", "") or settings.notion_api_key
            parent_page_id = init_data.get("parent_page_id", "") or settings.notion_parent_page_id
            if not notion_token or len(notion_token) < 5:
                await websocket.send_json({"type": "error", "content": "유효한 Notion 토큰이 필요합니다."})
                await websocket.close(code=4002)
                return
            agent = AgentOrchestrator(
                notion_token=notion_token,
                parent_page_id=parent_page_id,
                ai_key=init_data.get("ai_key", ""),
                ai_model=init_data.get("ai_model", ""),
            )
            await websocket.send_json({"type": "system", "content": "연결 완료! 어떤 템플릿을 만들어드릴까요?"})
        except asyncio.TimeoutError:
            await websocket.send_json({"type": "error", "content": "연결 시간 초과. init 메시지를 보내주세요."})
            await websocket.close(code=4003)
            return
        except (json.JSONDecodeError, Exception):
            await websocket.send_json({"type": "error", "content": "잘못된 메시지 형식입니다."})
            await websocket.close(code=4004)
            return

        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "content": "JSON 형식이 아닙니다."})
                continue

            # 메시지 Rate Limiting
            now = asyncio.get_event_loop().time()
            message_timestamps = [t for t in message_timestamps if now - t < 60]
            if len(message_timestamps) >= WS_MESSAGE_RATE_LIMIT:
                await websocket.send_json(
                    {"type": "error", "content": "메시지 전송 한도 초과. 잠시 후 다시 시도해주세요."}
                )
                continue
            message_timestamps.append(now)

            msg_type = data.get("type", "message")
            content = data.get("content", "")

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
                    logger.error(f"[Agent 에러] {e}", exc_info=True)
                    try:
                        await websocket.send_json({"type": "error", "content": sanitize_error(e)})
                    except Exception:
                        pass

            process_task = asyncio.create_task(_run_process(agent, content))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"[WebSocket 에러] {e}", exc_info=True)
        try:
            await websocket.send_json({"type": "error", "content": sanitize_error(e)})
        except Exception:
            pass
    finally:
        _ws_active[ip] = max(0, _ws_active[ip] - 1)
        if _ws_active[ip] == 0:
            _ws_active.pop(ip, None)
        if process_task and not process_task.done():
            process_task.cancel()
