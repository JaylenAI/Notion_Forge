"""PremiumJudge 단위 테스트 (Phase A1) — provider 주입으로 네트워크 없이 검증."""

from app.agent.premium_judge import (
    JudgeVerdict,
    _parse_verdict,
    _truthy,
    judge_blueprint,
    summarize_blueprint,
)

_VERDICT = {
    "verdicts": [
        {"criterion": "domain_fit", "pass": True, "reason": "적합"},
        {"criterion": "naming_quality", "pass": True, "reason": "전문적"},
        {"criterion": "layout_sense", "pass": False, "reason": "산만"},
        {"criterion": "completeness", "pass": True, "reason": "충분"},
        {"criterion": "willingness_to_pay", "pass": True, "reason": "지불의사"},
    ],
    "overall_pass": True,
    "estimated_band": "$20-49",
}


class _FakeProvider:
    name = "fake"

    def __init__(self, response):
        self._response = response

    async def call_with_retry(self, system, user, model="", timeout=30.0):
        if isinstance(self._response, Exception):
            raise self._response
        return self._response


def _blueprint():
    return {
        "metadata": {"title": "CRM 대시보드", "template_type": "crm", "color_theme": "blue"},
        "main_page": {"title": "CRM 대시보드"},
        "blocks": [{"type": "callout", "text": "환영"}, {"type": "database_ref", "db_index": 0}],
        "databases": [
            {
                "title": "고객",
                "properties": {"고객명": "title", "딜": {"type": "relation", "target_db_index": 1}},
                "views": [{"type": "table"}],
                "sample_items": [{"고객명": "A"}],
            },
        ],
        "sub_pages": [{"title": "시작하기"}],
    }


def test_truthy_variants():
    assert _truthy(True) and _truthy("PASS") and _truthy("yes") and _truthy(1)
    assert not _truthy(False) and not _truthy("fail") and not _truthy(0) and not _truthy(None)


def test_summarize_includes_db_and_title():
    s = summarize_blueprint(_blueprint())
    assert "CRM 대시보드" in s
    assert "고객" in s
    assert "relation" in s


def test_parse_verdict_wellformed():
    v = _parse_verdict(_VERDICT)
    assert v is not None
    assert v.overall_pass is True
    assert v.pass_count == 4 and v.total == 5
    assert v.estimated_band == "$20-49"


def test_parse_verdict_derives_overall_when_missing():
    data = {k: vv for k, vv in _VERDICT.items() if k != "overall_pass"}
    v = _parse_verdict(data)
    assert v is not None and v.overall_pass is True  # 4/5 >= ceil(5*0.6)=3

    # 과반 미달이면 fail로 유도
    few = {
        "verdicts": [
            {"criterion": "a", "pass": False},
            {"criterion": "b", "pass": False},
            {"criterion": "c", "pass": True},
        ]
    }
    v2 = _parse_verdict(few)
    assert v2 is not None and v2.overall_pass is False


def test_parse_verdict_rejects_malformed():
    assert _parse_verdict(None) is None
    assert _parse_verdict({"foo": "bar"}) is None  # verdicts 없음
    assert _parse_verdict({"verdicts": []}) is None


async def test_judge_blueprint_with_injected_provider():
    v = await judge_blueprint(_blueprint(), provider=_FakeProvider(_VERDICT))
    assert isinstance(v, JudgeVerdict)
    assert v.overall_pass is True
    md = v.to_metadata()
    assert md["judge_pass"] is True
    assert md["judge_pass_ratio"] == "4/5"
    assert "layout_sense" in md["judge_fails"]


async def test_judge_skips_on_non_verdict_response():
    """provider가 blueprint류 dict를 반환하면(심사 형식 아님) graceful None."""
    v = await judge_blueprint(_blueprint(), provider=_FakeProvider({"databases": [], "blocks": []}))
    assert v is None


async def test_judge_skips_on_provider_error():
    v = await judge_blueprint(_blueprint(), provider=_FakeProvider(RuntimeError("429 rate limit")))
    assert v is None
