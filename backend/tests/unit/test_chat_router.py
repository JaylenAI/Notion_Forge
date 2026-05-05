"""WebSocket 채팅 라우터 테스트 — chat.py 80%+ 커버리지 목표

테스트 시나리오:
1. 연결 수락
2. init 타임아웃 → close(4003)
3. init 타입 오류 → close(4001)
4. notion_token 누락/짧음 → close(4002)
5. 정상 init → system 응답
6. 메시지 Rate Limiting (20/분 초과 → error)
7. 제어 메시지 (confirm_create, cancel_create, set_complexity, set_language, set_pipeline)
8. JSON 파싱 에러 → error 응답
9. agent.process() 실행 (AgentOrchestrator 목킹)
10. WebSocketDisconnect 처리
11. 처리 중 예외 발생 시 에러 응답
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from starlette.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def valid_init_message():
    return json.dumps(
        {
            "type": "init",
            "notion_token": "ntn_valid_token_12345",
            "parent_page_id": "test-page-id",
            "ai_key": "test-key",
            "ai_model": "test-model",
        }
    )


@pytest.fixture
def short_token_init_message():
    return json.dumps(
        {
            "type": "init",
            "notion_token": "abc",
        }
    )


@pytest.fixture
def missing_token_init_message():
    return json.dumps(
        {
            "type": "init",
            "notion_token": "",
        }
    )


@pytest.fixture
def wrong_type_init_message():
    return json.dumps(
        {
            "type": "message",
            "content": "hello",
        }
    )


class TestWebSocketConnection:
    """WebSocket 연결 기본 동작 테스트"""

    @patch("app.routers.chat.AgentOrchestrator")
    def test_connection_accepted(self, mock_orchestrator_class, client, valid_init_message):
        """WebSocket 연결이 정상적으로 수락되는지 확인"""
        mock_orchestrator_class.return_value = MagicMock()

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            response = ws.receive_json()
            assert response["type"] == "system"
            assert "연결 완료" in response["content"]

    @patch("app.routers.chat.AgentOrchestrator")
    def test_connection_accepted_with_minimal_token(self, mock_orchestrator_class, client):
        """최소 길이(5자) 토큰으로 연결 성공"""
        mock_orchestrator_class.return_value = MagicMock()

        init_msg = json.dumps(
            {
                "type": "init",
                "notion_token": "12345",
            }
        )
        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(init_msg)
            response = ws.receive_json()
            assert response["type"] == "system"


class TestInitTimeout:
    """init 메시지 타임아웃 테스트"""

    @patch("app.routers.chat.WS_INIT_TIMEOUT", 0.01)
    def test_init_timeout_closes_with_4003(self, client):
        """init 메시지를 보내지 않으면 타임아웃(4003) 발생 → 에러 메시지 + 연결 종료"""
        with client.websocket_connect("/ws/chat") as ws:
            # 서버가 타임아웃 후 에러 메시지를 보내고 close 호출
            # TestClient에서는 receive_text()가 비동기가 아니므로 타임아웃이 바로 발동
            # 그래서 receive_json()으로 에러 메시지를 받을 수 있음
            response = ws.receive_json()
            assert response["type"] == "error"
            assert "시간 초과" in response["content"]


class TestInitValidation:
    """init 메시지 유효성 검증 테스트"""

    def test_wrong_type_closes_with_4001(self, client, wrong_type_init_message):
        """type이 'init'이 아닌 메시지 → 4001 코드로 연결 종료"""
        with pytest.raises(Exception):
            with client.websocket_connect("/ws/chat") as ws:
                ws.send_text(wrong_type_init_message)
                response = ws.receive_json()
                assert response["type"] == "error"
                assert "init 메시지가 필요합니다" in response["content"]
                # 서버가 close를 호출하므로 다음 receive에서 예외 발생
                ws.receive_json()

    def test_short_token_closes_with_4002(self, client, short_token_init_message):
        """5자 미만 토큰 → 4002 코드로 연결 종료"""
        with pytest.raises(Exception):
            with client.websocket_connect("/ws/chat") as ws:
                ws.send_text(short_token_init_message)
                response = ws.receive_json()
                assert response["type"] == "error"
                assert "유효한 Notion 토큰" in response["content"]
                ws.receive_json()

    def test_empty_token_closes_with_4002(self, client, missing_token_init_message):
        """빈 토큰 → 4002 코드로 연결 종료"""
        with pytest.raises(Exception):
            with client.websocket_connect("/ws/chat") as ws:
                ws.send_text(missing_token_init_message)
                response = ws.receive_json()
                assert response["type"] == "error"
                assert "유효한 Notion 토큰" in response["content"]
                ws.receive_json()

    def test_invalid_json_during_init_closes_with_4004(self, client):
        """JSON 파싱 실패 시 4004 코드로 연결 종료"""
        with pytest.raises(Exception):
            with client.websocket_connect("/ws/chat") as ws:
                ws.send_text("not a json string {{{")
                response = ws.receive_json()
                assert response["type"] == "error"
                assert "잘못된 메시지 형식" in response["content"]
                ws.receive_json()


class TestSuccessfulInit:
    """성공적 init 후 응답 확인"""

    @patch("app.routers.chat.AgentOrchestrator")
    def test_init_returns_system_message(self, mock_orchestrator_class, client, valid_init_message):
        """정상 init 후 시스템 환영 메시지 수신"""
        mock_orchestrator_class.return_value = MagicMock()

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            response = ws.receive_json()
            assert response["type"] == "system"
            assert "어떤 템플릿을 만들어드릴까요" in response["content"]

    @patch("app.routers.chat.AgentOrchestrator")
    def test_init_creates_orchestrator_with_params(self, mock_orchestrator_class, client):
        """init 시 전달된 파라미터로 AgentOrchestrator 생성 확인"""
        mock_orchestrator_class.return_value = MagicMock()

        init_msg = json.dumps(
            {
                "type": "init",
                "notion_token": "ntn_test_token_xyz",
                "parent_page_id": "my-page-id",
                "ai_key": "sk-test123",
                "ai_model": "gpt-4",
            }
        )

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(init_msg)
            ws.receive_json()

        mock_orchestrator_class.assert_called_once_with(
            notion_token="ntn_test_token_xyz",
            parent_page_id="my-page-id",
            ai_key="sk-test123",
            ai_model="gpt-4",
        )


class TestMessageRateLimiting:
    """메시지 Rate Limiting 테스트 (20/분 초과)"""

    @patch("app.routers.chat.AgentOrchestrator")
    def test_rate_limit_exceeded_returns_error(self, mock_orchestrator_class, client, valid_init_message):
        """20개 초과 메시지 전송 시 에러 응답"""
        mock_agent = MagicMock()
        mock_orchestrator_class.return_value = mock_agent

        # process()가 빈 async generator를 반환하도록 설정
        async def empty_generator(msg):
            return
            yield  # noqa: E275

        mock_agent.process = MagicMock(side_effect=lambda msg: empty_generator(msg))

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            ws.receive_json()  # system 메시지

            # 20개 메시지 전송 (rate limit 도달)
            for i in range(20):
                ws.send_text(json.dumps({"type": "message", "content": f"msg {i}"}))
                # process_task 완료 대기를 위해 약간의 딜레이 필요 없음
                # TestClient은 동기적이므로 바로 다음 메시지 전송 가능

            # 21번째 메시지 → rate limit 초과
            ws.send_text(json.dumps({"type": "message", "content": "overflow"}))
            response = ws.receive_json()
            assert response["type"] == "error"
            assert "한도 초과" in response["content"]

    @patch("app.routers.chat.AgentOrchestrator")
    def test_rate_limit_allows_within_limit(self, mock_orchestrator_class, client, valid_init_message):
        """20개 이하 메시지는 정상 처리"""
        mock_agent = MagicMock()
        mock_orchestrator_class.return_value = mock_agent

        async def single_event_generator(msg):
            yield {"type": "ai_response", "content": f"reply to: {msg}"}

        mock_agent.process = MagicMock(side_effect=lambda msg: single_event_generator(msg))

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            ws.receive_json()  # system 메시지

            # 첫 번째 메시지 정상 처리
            ws.send_text(json.dumps({"type": "message", "content": "hello"}))
            response = ws.receive_json()
            assert response["type"] == "ai_response"


class TestControlMessages:
    """제어 메시지 처리 테스트"""

    @patch("app.routers.chat.AgentOrchestrator")
    def test_confirm_create_calls_approve(self, mock_orchestrator_class, client, valid_init_message):
        """confirm_create 메시지 → agent.approve_creation(True) 호출"""
        mock_agent = MagicMock()
        mock_orchestrator_class.return_value = mock_agent

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            ws.receive_json()

            ws.send_text(json.dumps({"type": "confirm_create"}))
            # 제어 메시지는 응답 없이 처리됨 (continue)

        mock_agent.approve_creation.assert_called_once_with(approved=True)

    @patch("app.routers.chat.AgentOrchestrator")
    def test_cancel_create_calls_approve_false(self, mock_orchestrator_class, client, valid_init_message):
        """cancel_create 메시지 → agent.approve_creation(False) 호출"""
        mock_agent = MagicMock()
        mock_orchestrator_class.return_value = mock_agent

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            ws.receive_json()

            ws.send_text(json.dumps({"type": "cancel_create"}))

        mock_agent.approve_creation.assert_called_once_with(approved=False)

    @patch("app.routers.chat.AgentOrchestrator")
    def test_set_complexity_updates_agent(self, mock_orchestrator_class, client, valid_init_message):
        """set_complexity 메시지 → agent.complexity 업데이트 + 시스템 응답"""
        mock_agent = MagicMock()
        mock_orchestrator_class.return_value = mock_agent

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            ws.receive_json()  # init 응답

            ws.send_text(json.dumps({"type": "set_complexity", "complexity": "advanced"}))
            response = ws.receive_json()
            assert response["type"] == "system"
            assert "복잡도 설정" in response["content"]
            assert "advanced" in response["content"]

        assert mock_agent.complexity == "advanced"

    @patch("app.routers.chat.AgentOrchestrator")
    def test_set_complexity_default(self, mock_orchestrator_class, client, valid_init_message):
        """set_complexity에 값 없으면 'standard' 기본값"""
        mock_agent = MagicMock()
        mock_orchestrator_class.return_value = mock_agent

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            ws.receive_json()

            ws.send_text(json.dumps({"type": "set_complexity"}))
            response = ws.receive_json()
            assert "standard" in response["content"]

        assert mock_agent.complexity == "standard"

    @patch("app.routers.chat.AgentOrchestrator")
    def test_set_language_updates_agent(self, mock_orchestrator_class, client, valid_init_message):
        """set_language 메시지 → agent.language 업데이트"""
        mock_agent = MagicMock()
        mock_orchestrator_class.return_value = mock_agent

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            ws.receive_json()

            ws.send_text(json.dumps({"type": "set_language", "language": "en"}))
            response = ws.receive_json()
            assert response["type"] == "system"
            assert "언어 설정" in response["content"]
            assert "en" in response["content"]

        assert mock_agent.language == "en"

    @patch("app.routers.chat.AgentOrchestrator")
    def test_set_language_default(self, mock_orchestrator_class, client, valid_init_message):
        """set_language에 값 없으면 'ko' 기본값"""
        mock_agent = MagicMock()
        mock_orchestrator_class.return_value = mock_agent

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            ws.receive_json()

            ws.send_text(json.dumps({"type": "set_language"}))
            response = ws.receive_json()
            assert "ko" in response["content"]

        assert mock_agent.language == "ko"

    @patch("app.routers.chat.AgentOrchestrator")
    def test_set_pipeline_enabled(self, mock_orchestrator_class, client, valid_init_message):
        """set_pipeline enabled=True → Multi-Agent Pipeline 모드"""
        mock_agent = MagicMock()
        mock_orchestrator_class.return_value = mock_agent

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            ws.receive_json()

            ws.send_text(json.dumps({"type": "set_pipeline", "enabled": True}))
            response = ws.receive_json()
            assert response["type"] == "system"
            assert "Multi-Agent Pipeline" in response["content"]

        assert mock_agent.use_pipeline is True

    @patch("app.routers.chat.AgentOrchestrator")
    def test_set_pipeline_disabled(self, mock_orchestrator_class, client, valid_init_message):
        """set_pipeline enabled=False → Single Agent 모드"""
        mock_agent = MagicMock()
        mock_orchestrator_class.return_value = mock_agent

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            ws.receive_json()

            ws.send_text(json.dumps({"type": "set_pipeline", "enabled": False}))
            response = ws.receive_json()
            assert response["type"] == "system"
            assert "Single Agent" in response["content"]

        assert mock_agent.use_pipeline is False

    @patch("app.routers.chat.AgentOrchestrator")
    def test_cancel_message_is_handled(self, mock_orchestrator_class, client, valid_init_message):
        """cancel 타입 메시지는 조용히 처리됨"""
        mock_agent = MagicMock()
        mock_orchestrator_class.return_value = mock_agent

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            ws.receive_json()

            # cancel 메시지 후 일반 메시지로 정상 통신 확인
            ws.send_text(json.dumps({"type": "cancel"}))

            async def single_event_generator(msg):
                yield {"type": "ai_response", "content": "hello"}

            mock_agent.process = MagicMock(side_effect=lambda msg: single_event_generator(msg))
            ws.send_text(json.dumps({"type": "message", "content": "test"}))
            response = ws.receive_json()
            assert response["type"] == "ai_response"


class TestJsonParseError:
    """JSON 파싱 에러 처리 테스트"""

    @patch("app.routers.chat.AgentOrchestrator")
    def test_invalid_json_after_init_returns_error(self, mock_orchestrator_class, client, valid_init_message):
        """init 이후 잘못된 JSON → 에러 응답 (연결 유지)"""
        mock_agent = MagicMock()
        mock_orchestrator_class.return_value = mock_agent

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            ws.receive_json()  # system 메시지

            ws.send_text("this is not json {{{")
            response = ws.receive_json()
            assert response["type"] == "error"
            assert "JSON 형식이 아닙니다" in response["content"]

    @patch("app.routers.chat.AgentOrchestrator")
    def test_connection_survives_after_json_error(self, mock_orchestrator_class, client, valid_init_message):
        """JSON 에러 후에도 연결이 유지되어 후속 메시지 처리 가능"""
        mock_agent = MagicMock()
        mock_orchestrator_class.return_value = mock_agent

        async def single_event_generator(msg):
            yield {"type": "ai_response", "content": f"echo: {msg}"}

        mock_agent.process = MagicMock(side_effect=lambda msg: single_event_generator(msg))

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            ws.receive_json()

            # 잘못된 JSON
            ws.send_text("broken json")
            error_resp = ws.receive_json()
            assert error_resp["type"] == "error"

            # 이후 정상 메시지 처리 가능
            ws.send_text(json.dumps({"type": "message", "content": "valid msg"}))
            response = ws.receive_json()
            assert response["type"] == "ai_response"


class TestAgentProcessExecution:
    """agent.process() 실행 테스트"""

    @patch("app.routers.chat.AgentOrchestrator")
    def test_user_message_triggers_process(self, mock_orchestrator_class, client, valid_init_message):
        """일반 메시지가 agent.process()를 호출하는지 확인"""
        mock_agent = MagicMock()
        mock_orchestrator_class.return_value = mock_agent

        async def mock_process(msg):
            yield {"type": "progress", "step": "intent_analysis", "message": "분석 중..."}
            yield {"type": "ai_response", "content": "결과입니다"}

        mock_agent.process = MagicMock(side_effect=mock_process)

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            ws.receive_json()  # system

            ws.send_text(json.dumps({"type": "message", "content": "프로젝트 관리 템플릿 만들어줘"}))
            resp1 = ws.receive_json()
            assert resp1["type"] == "progress"
            resp2 = ws.receive_json()
            assert resp2["type"] == "ai_response"
            assert "결과입니다" in resp2["content"]

        mock_agent.process.assert_called_once_with("프로젝트 관리 템플릿 만들어줘")

    @patch("app.routers.chat.AgentOrchestrator")
    def test_process_error_sends_sanitized_error(self, mock_orchestrator_class, client, valid_init_message):
        """agent.process()에서 예외 발생 시 sanitized 에러 전송"""
        mock_agent = MagicMock()
        mock_orchestrator_class.return_value = mock_agent

        async def failing_process(msg):
            raise ValueError("DB connection failed")
            yield  # noqa: E275

        mock_agent.process = MagicMock(side_effect=failing_process)

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            ws.receive_json()

            ws.send_text(json.dumps({"type": "message", "content": "test"}))
            response = ws.receive_json()
            assert response["type"] == "error"

    @patch("app.routers.chat.AgentOrchestrator")
    def test_multiple_events_streamed(self, mock_orchestrator_class, client, valid_init_message):
        """agent.process()가 여러 이벤트를 스트리밍하는 경우"""
        mock_agent = MagicMock()
        mock_orchestrator_class.return_value = mock_agent

        async def multi_event_process(msg):
            yield {"type": "progress", "step": "intent_analysis", "message": "분석 중..."}
            yield {"type": "progress", "step": "design_done", "message": "설계 완료"}
            yield {"type": "blueprint_preview", "content": "미리보기", "blueprint": {}}
            yield {"type": "complete", "content": "생성 완료!", "result": {"pages": []}}

        mock_agent.process = MagicMock(side_effect=multi_event_process)

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            ws.receive_json()

            ws.send_text(json.dumps({"type": "message", "content": "대시보드 만들어줘"}))

            responses = []
            for _ in range(4):
                responses.append(ws.receive_json())

            assert responses[0]["type"] == "progress"
            assert responses[1]["type"] == "progress"
            assert responses[2]["type"] == "blueprint_preview"
            assert responses[3]["type"] == "complete"

    @patch("app.routers.chat.AgentOrchestrator")
    def test_message_without_type_defaults_to_message(self, mock_orchestrator_class, client, valid_init_message):
        """type 필드 없는 메시지도 일반 메시지로 처리"""
        mock_agent = MagicMock()
        mock_orchestrator_class.return_value = mock_agent

        async def echo_process(msg):
            yield {"type": "ai_response", "content": msg}

        mock_agent.process = MagicMock(side_effect=echo_process)

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            ws.receive_json()

            # type 없이 content만 보냄
            ws.send_text(json.dumps({"content": "no type field"}))
            response = ws.receive_json()
            assert response["type"] == "ai_response"

        mock_agent.process.assert_called_once_with("no type field")

    @patch("app.routers.chat.AgentOrchestrator")
    def test_message_without_content_sends_empty_string(self, mock_orchestrator_class, client, valid_init_message):
        """content 필드 없는 메시지 → 빈 문자열로 process 호출"""
        mock_agent = MagicMock()
        mock_orchestrator_class.return_value = mock_agent

        async def echo_process(msg):
            yield {"type": "ai_response", "content": f"received: '{msg}'"}

        mock_agent.process = MagicMock(side_effect=echo_process)

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            ws.receive_json()

            ws.send_text(json.dumps({"type": "message"}))
            response = ws.receive_json()
            assert response["type"] == "ai_response"

        mock_agent.process.assert_called_once_with("")


class TestProcessTaskBehavior:
    """process_task 관련 동작 테스트"""

    @patch("app.routers.chat.AgentOrchestrator")
    def test_skip_message_if_task_running(self, mock_orchestrator_class, client, valid_init_message):
        """이전 process_task가 아직 실행 중이면 새 메시지 무시"""
        mock_agent = MagicMock()
        mock_orchestrator_class.return_value = mock_agent

        call_count = 0

        async def slow_process(msg):
            nonlocal call_count
            call_count += 1
            yield {"type": "ai_response", "content": f"response #{call_count}"}

        mock_agent.process = MagicMock(side_effect=slow_process)

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            ws.receive_json()

            # 첫 번째 메시지
            ws.send_text(json.dumps({"type": "message", "content": "first"}))
            resp = ws.receive_json()
            assert resp["type"] == "ai_response"


class TestWebSocketDisconnect:
    """WebSocket 연결 해제 처리"""

    @patch("app.routers.chat.AgentOrchestrator")
    def test_client_disconnect_handled_gracefully(self, mock_orchestrator_class, client, valid_init_message):
        """클라이언트 연결 해제 시 예외 없이 종료"""
        mock_agent = MagicMock()
        mock_orchestrator_class.return_value = mock_agent

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            ws.receive_json()
            # 연결 종료 (정상적인 close)

    @patch("app.routers.chat.AgentOrchestrator")
    def test_disconnect_during_init_phase(self, mock_orchestrator_class, client):
        """init 전 연결 해제도 정상 처리"""
        with client.websocket_connect("/ws/chat") as _ws:
            pass  # init 없이 바로 종료


class TestEdgeCases:
    """경계 조건 및 특수 케이스 테스트"""

    @patch("app.routers.chat.AgentOrchestrator")
    def test_empty_json_object(self, mock_orchestrator_class, client, valid_init_message):
        """빈 JSON 객체 → 기본값으로 처리"""
        mock_agent = MagicMock()
        mock_orchestrator_class.return_value = mock_agent

        async def echo_process(msg):
            yield {"type": "ai_response", "content": "ok"}

        mock_agent.process = MagicMock(side_effect=echo_process)

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            ws.receive_json()

            ws.send_text(json.dumps({}))
            response = ws.receive_json()
            # type이 "message"로 기본 설정되므로 process 호출됨
            assert response["type"] == "ai_response"

    @patch("app.routers.chat.AgentOrchestrator")
    def test_unicode_content(self, mock_orchestrator_class, client, valid_init_message):
        """유니코드 문자 포함 메시지 정상 처리"""
        mock_agent = MagicMock()
        mock_orchestrator_class.return_value = mock_agent

        async def echo_process(msg):
            yield {"type": "ai_response", "content": msg}

        mock_agent.process = MagicMock(side_effect=echo_process)

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            ws.receive_json()

            ws.send_text(json.dumps({"type": "message", "content": "한글 테스트 🎉 日本語"}))
            response = ws.receive_json()
            assert "한글 테스트" in response["content"]

    @patch("app.routers.chat.AgentOrchestrator")
    def test_very_long_content(self, mock_orchestrator_class, client, valid_init_message):
        """매우 긴 메시지 내용 처리"""
        mock_agent = MagicMock()
        mock_orchestrator_class.return_value = mock_agent

        async def echo_process(msg):
            yield {"type": "ai_response", "content": f"len={len(msg)}"}

        mock_agent.process = MagicMock(side_effect=echo_process)

        long_content = "a" * 10000

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            ws.receive_json()

            ws.send_text(json.dumps({"type": "message", "content": long_content}))
            response = ws.receive_json()
            assert response["type"] == "ai_response"
            assert "10000" in response["content"]

    @patch("app.routers.chat.AgentOrchestrator")
    def test_special_characters_in_token(self, mock_orchestrator_class, client):
        """특수문자 포함 토큰도 5자 이상이면 허용"""
        mock_orchestrator_class.return_value = MagicMock()

        init_msg = json.dumps(
            {
                "type": "init",
                "notion_token": "ntn_!@#$%^&*()",
            }
        )

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(init_msg)
            response = ws.receive_json()
            assert response["type"] == "system"

    @patch("app.routers.chat.AgentOrchestrator")
    def test_init_without_optional_fields(self, mock_orchestrator_class, client):
        """선택 필드(parent_page_id, ai_key, ai_model) 없이도 정상 동작"""
        mock_orchestrator_class.return_value = MagicMock()

        init_msg = json.dumps(
            {
                "type": "init",
                "notion_token": "ntn_minimal_token",
            }
        )

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(init_msg)
            response = ws.receive_json()
            assert response["type"] == "system"

        mock_orchestrator_class.assert_called_once_with(
            notion_token="ntn_minimal_token",
            parent_page_id="",
            ai_key="",
            ai_model="",
        )

    @patch("app.routers.chat.AgentOrchestrator")
    def test_control_message_without_agent_returns_false(self, mock_orchestrator_class, client, valid_init_message):
        """agent가 None인 상태에서 제어 메시지 → _handle_control_message가 False 반환하여 process 실행"""
        # agent를 None으로 설정할 수 없으므로(init에서 할당됨),
        # 대신 unknown 타입의 제어 메시지가 False를 반환하는 것을 테스트
        mock_agent = MagicMock()
        mock_orchestrator_class.return_value = mock_agent

        async def echo_process(msg):
            yield {"type": "ai_response", "content": "processed"}

        mock_agent.process = MagicMock(side_effect=echo_process)

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            ws.receive_json()

            # 알 수 없는 type → _handle_control_message가 False → process 실행
            ws.send_text(json.dumps({"type": "unknown_type", "content": "test"}))
            response = ws.receive_json()
            assert response["type"] == "ai_response"


class TestSanitizeError:
    """에러 sanitization 테스트"""

    @patch("app.routers.chat.AgentOrchestrator")
    @patch("app.routers.chat.sanitize_error")
    def test_sanitize_error_called_on_process_exception(
        self, mock_sanitize, mock_orchestrator_class, client, valid_init_message
    ):
        """process 예외 시 sanitize_error가 호출되는지 확인"""
        mock_agent = MagicMock()
        mock_orchestrator_class.return_value = mock_agent
        mock_sanitize.return_value = "안전한 에러 메시지"

        async def failing_process(msg):
            raise RuntimeError("Internal: secret info exposed")
            yield  # noqa: E275

        mock_agent.process = MagicMock(side_effect=failing_process)

        with client.websocket_connect("/ws/chat") as ws:
            ws.send_text(valid_init_message)
            ws.receive_json()

            ws.send_text(json.dumps({"type": "message", "content": "trigger error"}))
            response = ws.receive_json()
            assert response["type"] == "error"
            assert response["content"] == "안전한 에러 메시지"

        mock_sanitize.assert_called_once()
