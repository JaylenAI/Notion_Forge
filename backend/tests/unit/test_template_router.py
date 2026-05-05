"""Template Router 테스트: 생성/스트리밍/미리보기/문서업로드 엔드포인트"""

import asyncio
import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.middleware import RateLimitMiddleware
from app.main import app


def _reset_rate_limiter():
    """앱의 RateLimitMiddleware 내부 상태 초기화"""
    current = app.middleware_stack
    while current:
        if isinstance(current, RateLimitMiddleware):
            current._requests.clear()
            break
        current = getattr(current, "app", None)


@pytest.fixture
async def client():
    _reset_rate_limiter()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


VALID_REQUEST = {
    "prompt": "프로젝트 관리 대시보드 만들어줘",
    "notion_token": "ntn_test_token_12345",
    "parent_page_id": "abc12345-1234-1234-1234-123456789012",
}


class TestGenerateEndpoint:
    """POST /api/templates/generate"""

    async def test_generate_success(self, client):
        """정상 생성 시 success=True, notion_url, summary 반환"""
        mock_events = [
            {"type": "approval_request"},
            {
                "type": "complete",
                "result": {
                    "main_url": "https://notion.so/test-page",
                    "pages": [{"id": "page-001"}],
                    "databases": [{"id": "db-001"}],
                    "blocks": 15,
                },
            },
        ]

        async def mock_process(prompt):
            for event in mock_events:
                yield event

        with patch("app.routers.template.AgentOrchestrator") as mock_orch:
            mock_instance = MagicMock()
            mock_instance.process = mock_process
            mock_instance.approve_creation = MagicMock()
            mock_orch.return_value = mock_instance

            resp = await client.post("/api/templates/generate", json=VALID_REQUEST)

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["notion_url"] == "https://notion.so/test-page"
        assert data["page_id"] == "page-001"
        assert data["summary"]["pages"] == 1
        assert data["summary"]["databases"] == 1
        assert data["summary"]["blocks"] == 15

    async def test_generate_question_response(self, client):
        """에이전트가 질문을 던지면 success=False + question 반환"""

        async def mock_process(prompt):
            yield {"type": "question", "content": "어떤 색상을 선호하시나요?"}

        with patch("app.routers.template.AgentOrchestrator") as mock_orch:
            mock_instance = MagicMock()
            mock_instance.process = mock_process
            mock_orch.return_value = mock_instance

            resp = await client.post("/api/templates/generate", json=VALID_REQUEST)

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False
        assert data["summary"]["question"] == "어떤 색상을 선호하시나요?"

    async def test_generate_no_result(self, client):
        """이벤트가 없으면 success=False"""

        async def mock_process(prompt):
            return
            yield  # noqa: E275

        with patch("app.routers.template.AgentOrchestrator") as mock_orch:
            mock_instance = MagicMock()
            mock_instance.process = mock_process
            mock_orch.return_value = mock_instance

            resp = await client.post("/api/templates/generate", json=VALID_REQUEST)

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False

    async def test_generate_timeout(self, client):
        """타임아웃 발생 시 적절한 에러 메시지 반환"""

        async def mock_process(prompt):
            await asyncio.sleep(300)
            yield {"type": "complete", "result": {}}

        with patch("app.routers.template.AgentOrchestrator") as mock_orch:
            mock_instance = MagicMock()
            mock_instance.process = mock_process
            mock_orch.return_value = mock_instance

            with patch("app.routers.template.GENERATE_TIMEOUT", 0.01):
                resp = await client.post("/api/templates/generate", json=VALID_REQUEST)

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False
        assert "초과" in data["summary"]["error"]

    async def test_generate_validates_empty_prompt(self, client):
        """빈 프롬프트는 422 반환"""
        req = {**VALID_REQUEST, "prompt": ""}
        resp = await client.post("/api/templates/generate", json=req)
        assert resp.status_code == 422

    async def test_generate_validates_short_prompt(self, client):
        """1자 프롬프트는 422 반환 (min_length=2)"""
        req = {**VALID_REQUEST, "prompt": "a"}
        resp = await client.post("/api/templates/generate", json=req)
        assert resp.status_code == 422

    async def test_generate_validates_missing_token(self, client):
        """notion_token 누락 시 422"""
        req = {**VALID_REQUEST, "notion_token": ""}
        resp = await client.post("/api/templates/generate", json=req)
        assert resp.status_code == 422

    async def test_generate_validates_invalid_page_id(self, client):
        """유효하지 않은 parent_page_id 패턴 시 422"""
        req = {**VALID_REQUEST, "parent_page_id": "invalid!chars@here"}
        resp = await client.post("/api/templates/generate", json=req)
        assert resp.status_code == 422


class TestStreamEndpoint:
    """POST /api/templates/generate/stream"""

    async def test_stream_returns_event_stream(self, client):
        """SSE 응답이 text/event-stream 타입으로 반환"""

        async def mock_process(prompt):
            yield {"type": "progress", "step": "planning", "message": "계획 수립 중"}
            yield {
                "type": "complete",
                "result": {
                    "main_url": "https://notion.so/streamed",
                    "pages": [{"id": "p1"}],
                    "databases": [],
                    "blocks": 5,
                },
            }

        with patch("app.routers.template.AgentOrchestrator") as mock_orch:
            mock_instance = MagicMock()
            mock_instance.process = mock_process
            mock_orch.return_value = mock_instance

            resp = await client.post("/api/templates/generate/stream", json=VALID_REQUEST)

        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers["content-type"]

    async def test_stream_emits_progress_events(self, client):
        """진행 이벤트가 data: 형태로 출력"""

        async def mock_process(prompt):
            yield {"type": "progress", "step": "building", "message": "블록 생성 중"}
            yield {
                "type": "complete",
                "result": {
                    "main_url": "https://notion.so/x",
                    "pages": [{"id": "p1"}],
                    "databases": [],
                    "blocks": 3,
                },
            }

        with patch("app.routers.template.AgentOrchestrator") as mock_orch:
            mock_instance = MagicMock()
            mock_instance.process = mock_process
            mock_orch.return_value = mock_instance

            resp = await client.post("/api/templates/generate/stream", json=VALID_REQUEST)

        body = resp.text
        assert "progress" in body
        assert "building" in body

    async def test_stream_error_event(self, client):
        """에러 이벤트 발생 시 error 타입 SSE 전송"""

        async def mock_process(prompt):
            yield {"type": "error", "content": "API 키가 만료되었습니다"}

        with patch("app.routers.template.AgentOrchestrator") as mock_orch:
            mock_instance = MagicMock()
            mock_instance.process = mock_process
            mock_orch.return_value = mock_instance

            resp = await client.post("/api/templates/generate/stream", json=VALID_REQUEST)

        body = resp.text
        assert "error" in body
        assert "만료" in body

    async def test_stream_exception_handling(self, client):
        """스트리밍 중 예외 발생 시 에러 SSE 전송"""

        async def mock_process(prompt):
            raise RuntimeError("unexpected failure")
            yield  # noqa

        with patch("app.routers.template.AgentOrchestrator") as mock_orch:
            mock_instance = MagicMock()
            mock_instance.process = mock_process
            mock_orch.return_value = mock_instance

            resp = await client.post("/api/templates/generate/stream", json=VALID_REQUEST)

        body = resp.text
        assert "error" in body

    async def test_stream_validates_input(self, client):
        """잘못된 입력에 대해 422"""
        resp = await client.post(
            "/api/templates/generate/stream",
            json={"prompt": "", "notion_token": "", "parent_page_id": ""},
        )
        assert resp.status_code == 422


class TestPreviewEndpoint:
    """POST /api/templates/preview"""

    async def test_preview_returns_blueprint(self, client):
        """정상 프롬프트로 blueprint 반환"""
        mock_blueprint = {
            "version": "3.0",
            "metadata": {"title": "프로젝트 관리"},
            "main_page": {"title": "프로젝트 관리"},
            "blocks": [],
            "databases": [],
        }

        with patch("app.routers.template.generate_blueprint", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = mock_blueprint

            resp = await client.post(
                "/api/templates/preview",
                json={"prompt": "프로젝트 관리 템플릿"},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert "blueprint" in data
        assert data["blueprint"]["version"] == "3.0"
        mock_gen.assert_called_once_with("프로젝트 관리 템플릿")

    async def test_preview_validates_empty_prompt(self, client):
        """빈 프롬프트 시 422"""
        resp = await client.post("/api/templates/preview", json={"prompt": ""})
        assert resp.status_code == 422

    async def test_preview_validates_short_prompt(self, client):
        """1자 프롬프트 시 422 (min_length=2)"""
        resp = await client.post("/api/templates/preview", json={"prompt": "a"})
        assert resp.status_code == 422


class TestDocumentToNotionEndpoint:
    """POST /api/templates/document-to-notion"""

    async def test_upload_txt_file(self, client):
        """txt 파일 업로드 시 정상 처리"""
        mock_parsed = {
            "text_content": "sample text content",
            "hint": "텍스트 문서를 분석했습니다",
            "blocks": [],
        }
        mock_blueprint = {
            "version": "3.0",
            "blocks": [{"type": "heading_1", "text": "Test"}],
        }

        with (
            patch("app.agent.document_parser.parse_document", return_value=mock_parsed),
            patch(
                "app.agent.blueprint_generator.generate_blueprint", new_callable=AsyncMock, return_value=mock_blueprint
            ),
        ):
            file_content = b"Hello, this is test content for NotionForge."
            resp = await client.post(
                "/api/templates/document-to-notion",
                files={"file": ("test.txt", io.BytesIO(file_content), "text/plain")},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "blueprint" in data

    async def test_upload_csv_file(self, client):
        """csv 파일 업로드 시 DB 블루프린트 생성"""
        mock_parsed = {
            "properties": [
                {"name": "이름", "type": "title"},
                {"name": "상태", "type": "select"},
            ],
            "db_title": "Imported CSV",
            "hint": "CSV 데이터를 분석했습니다",
            "sample_items": [{"이름": "항목1"}],
        }

        with patch("app.agent.document_parser.parse_document", return_value=mock_parsed):
            file_content = b"name,status\nitem1,active\nitem2,done"
            resp = await client.post(
                "/api/templates/document-to-notion",
                files={"file": ("data.csv", io.BytesIO(file_content), "text/csv")},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["blueprint"]["databases"][0]["title"] == "Imported CSV"

    async def test_upload_md_file(self, client):
        """md 파일 업로드 정상 처리"""
        mock_parsed = {
            "text_content": "# Heading\nSome markdown content",
            "hint": "마크다운 문서입니다",
            "blocks": [{"type": "heading_1", "text": "Heading"}],
        }
        mock_blueprint = {
            "version": "3.0",
            "blocks": [],
        }

        with (
            patch("app.agent.document_parser.parse_document", return_value=mock_parsed),
            patch(
                "app.agent.blueprint_generator.generate_blueprint", new_callable=AsyncMock, return_value=mock_blueprint
            ),
        ):
            file_content = b"# Heading\nSome markdown content"
            resp = await client.post(
                "/api/templates/document-to-notion",
                files={"file": ("readme.md", io.BytesIO(file_content), "text/markdown")},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "blueprint" in data

    async def test_upload_pdf_file(self, client):
        """pdf 파일 업로드 정상 처리"""
        mock_parsed = {
            "text_content": "PDF extracted text",
            "hint": "PDF 문서를 분석했습니다",
            "blocks": [],
        }
        mock_blueprint = {"version": "3.0", "blocks": []}

        with (
            patch("app.agent.document_parser.parse_pdf_bytes", return_value=mock_parsed),
            patch(
                "app.agent.blueprint_generator.generate_blueprint", new_callable=AsyncMock, return_value=mock_blueprint
            ),
        ):
            file_content = b"%PDF-1.4 fake pdf content bytes"
            resp = await client.post(
                "/api/templates/document-to-notion",
                files={"file": ("document.pdf", io.BytesIO(file_content), "application/pdf")},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    async def test_upload_unsupported_extension_returns_415(self, client):
        """지원하지 않는 확장자(.docx 등)는 415 반환"""
        file_content = b"some docx content"
        resp = await client.post(
            "/api/templates/document-to-notion",
            files={"file": ("file.docx", io.BytesIO(file_content), "application/vnd.openxmlformats")},
        )
        assert resp.status_code == 415
        data = resp.json()
        assert "지원하지 않는" in data["detail"]

    async def test_upload_exe_extension_returns_415(self, client):
        """실행 파일(.exe)은 415 반환"""
        file_content = b"\x00\x00\x00"
        resp = await client.post(
            "/api/templates/document-to-notion",
            files={"file": ("malware.exe", io.BytesIO(file_content), "application/octet-stream")},
        )
        assert resp.status_code == 415

    async def test_upload_no_extension_returns_415(self, client):
        """확장자가 없는 파일은 해당 확장자가 허용 목록에 없으므로 415"""
        file_content = b"content without extension"
        resp = await client.post(
            "/api/templates/document-to-notion",
            files={"file": ("noextension", io.BytesIO(file_content), "text/plain")},
        )
        assert resp.status_code == 415

    async def test_upload_oversized_file_returns_413(self, client):
        """10MB 초과 파일은 413 반환"""
        file_content = b"x" * (10 * 1024 * 1024 + 1)  # 10MB + 1 byte
        resp = await client.post(
            "/api/templates/document-to-notion",
            files={"file": ("big.txt", io.BytesIO(file_content), "text/plain")},
        )
        assert resp.status_code == 413
        data = resp.json()
        assert "10MB" in data["detail"]

    async def test_upload_exactly_10mb_succeeds(self, client):
        """정확히 10MB 파일은 허용"""
        file_content = b"x" * (10 * 1024 * 1024)  # exactly 10MB
        mock_parsed = {"text_content": "big text", "hint": "큰 파일", "blocks": []}
        mock_blueprint = {"version": "3.0", "blocks": []}

        with (
            patch("app.agent.document_parser.parse_document", return_value=mock_parsed),
            patch(
                "app.agent.blueprint_generator.generate_blueprint", new_callable=AsyncMock, return_value=mock_blueprint
            ),
        ):
            resp = await client.post(
                "/api/templates/document-to-notion",
                files={"file": ("exact.txt", io.BytesIO(file_content), "text/plain")},
            )

        assert resp.status_code == 200

    async def test_upload_empty_file(self, client):
        """빈 파일도 유효한 확장자면 처리 시도"""
        mock_parsed = {"text_content": "", "hint": "빈 파일", "blocks": []}
        mock_blueprint = {"version": "3.0", "blocks": []}

        with (
            patch("app.agent.document_parser.parse_document", return_value=mock_parsed),
            patch(
                "app.agent.blueprint_generator.generate_blueprint", new_callable=AsyncMock, return_value=mock_blueprint
            ),
        ):
            resp = await client.post(
                "/api/templates/document-to-notion",
                files={"file": ("empty.txt", io.BytesIO(b""), "text/plain")},
            )

        assert resp.status_code == 200


class TestPatternsEndpoint:
    """GET /api/templates/patterns"""

    async def test_list_patterns(self, client):
        """패턴 목록 반환"""
        resp = await client.get("/api/templates/patterns")
        assert resp.status_code == 200
        data = resp.json()
        assert "patterns" in data
        assert len(data["patterns"]) >= 5

    async def test_patterns_have_required_fields(self, client):
        """각 패턴에 id, name, icon, description 필수 필드 존재"""
        resp = await client.get("/api/templates/patterns")
        data = resp.json()
        for pattern in data["patterns"]:
            assert "id" in pattern
            assert "name" in pattern
            assert "icon" in pattern
            assert "description" in pattern
