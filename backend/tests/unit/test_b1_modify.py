"""B1 AI 대화형 수정 테스트 — LLM 분류기 + recolor + LLM 라우팅 (네트워크 없이 주입)."""

from app.agent import modify_classifier
from app.agent.modify_classifier import classify_modification
from app.agent.modify_handler import ModifyHandler
from app.schemas.blueprint import IntentResult


class _FakeProvider:
    def __init__(self, response):
        self._response = response

    async def call_with_retry(self, system, user, model="", timeout=20.0):
        if isinstance(self._response, Exception):
            raise self._response
        return self._response


class _FakeClient:
    """recolor 검증용 — get_block_children/update_block 기록."""

    def __init__(self, blocks=None):
        self._blocks = blocks or []
        self.updated: list[tuple[str, dict]] = []
        self.mock_mode = False

    async def get_block_children(self, block_id, page_size=100):
        return self._blocks

    async def update_block(self, block_id, block_data):
        self.updated.append((block_id, block_data))
        return {"id": block_id}


# ── 분류기 ──


async def test_classify_returns_operation():
    op = await classify_modification("파란색으로 바꿔줘", provider=_FakeProvider({"operation": "recolor"}))
    assert op == "recolor"


async def test_classify_rejects_invalid_operation():
    op = await classify_modification("뭐든", provider=_FakeProvider({"operation": "nonsense"}))
    assert op is None


async def test_classify_none_on_provider_error():
    op = await classify_modification("x", provider=_FakeProvider(RuntimeError("429")))
    assert op is None


async def test_classify_none_on_non_dict():
    op = await classify_modification("x", provider=_FakeProvider("not a dict"))
    assert op is None


# ── recolor 핸들러 ──


async def test_recolor_updates_themed_and_heading_only():
    rt = [{"type": "text", "text": {"content": "내용"}}]
    fake = _FakeClient(
        blocks=[
            {
                "id": "b1",
                "type": "callout",
                "callout": {"rich_text": rt, "color": "gray_background", "icon": {"emoji": "📌"}},
            },
            {"id": "b2", "type": "heading_1", "heading_1": {"rich_text": rt, "color": "default"}},
            {"id": "b3", "type": "divider", "divider": {}},
            {"id": "b4", "type": "quote", "quote": {"rich_text": rt, "color": "default"}},
        ]
    )
    h = ModifyHandler(fake)
    events = [e async for e in h._handle_recolor("파란색으로 바꿔줘", {"pages": [{"id": "p"}]})]

    ids = [u[0] for u in fake.updated]
    assert set(ids) == {"b1", "b2", "b4"}  # divider 제외
    callout = next(d for bid, d in fake.updated if bid == "b1")
    assert callout["callout"]["color"] == "blue_background"
    # Notion 필수 필드(rich_text) 보존 + callout icon 보존 (E2E 400 'rich_text undefined' 보정)
    assert callout["callout"]["rich_text"] == rt
    assert callout["callout"]["icon"] == {"emoji": "📌"}
    heading = next(d for bid, d in fake.updated if bid == "b2")
    assert heading["heading_1"]["color"] == "blue"
    assert heading["heading_1"]["rich_text"] == rt
    assert any(e.get("type") == "complete" for e in events)


async def test_recolor_asks_when_no_color():
    h = ModifyHandler(_FakeClient(blocks=[{"id": "b1", "type": "callout"}]))
    events = [e async for e in h._handle_recolor("색 바꿔줘", {"pages": [{"id": "p"}]})]
    assert any("어떤 색" in e.get("content", "") for e in events)
    # 색 미지정 → 변경 없음


# ── LLM 라우팅 통합 ──


async def test_handle_modify_routes_recolor_via_llm(monkeypatch):
    async def fake_classify(message, result=None, blueprint=None, ai_key="", ai_model="", provider=None):
        return "recolor"

    monkeypatch.setattr(modify_classifier, "classify_modification", fake_classify)

    fake = _FakeClient(blocks=[{"id": "b1", "type": "callout"}])
    h = ModifyHandler(fake)
    intent = IntentResult(intent="MODIFY", template_type="crm")
    events = [e async for e in h.handle_modify("파란색으로", intent, {"pages": [{"id": "p"}], "databases": []}, {})]
    # LLM이 recolor로 분류 → 블록 업데이트됨
    assert fake.updated and fake.updated[0][0] == "b1"
    assert any(e.get("type") == "complete" for e in events)
