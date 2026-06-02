"""PremiumJudge: 주관적 품질 LLM 심사 (Phase A1).

premium_rubric(결정적 구조 점수)가 못 잡는 **주관적 품질**을 LLM이 PASS/FAIL로 판정한다:
도메인 적합성, 네이밍 센스, 레이아웃 합리성, 완성도, 지불 의사.

원칙(리서치 2026):
- 이진 PASS/FAIL (1~5 Likert는 노이즈가 큼)
- self-preference bias 회피 위해 생성과 **다른 모델 패밀리** 권장
- provider 실패/미설정/예산초과 시 None 반환 (graceful skip — 생성 자체는 막지 않음)

provider.call()은 모든 구현이 generic extract_json을 쓰므로 임의 JSON verdict를 받는다.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("notionforge.premium_judge")

_CRITERIA = ("domain_fit", "naming_quality", "layout_sense", "completeness", "willingness_to_pay")

JUDGE_SYSTEM_PROMPT = """당신은 Notion 템플릿 마켓플레이스의 엄격한 심사관입니다.
아래 템플릿 구조 요약을 보고, $20-49에 실제로 팔 수 있는 수준인지 5개 기준으로 평가하세요.

평가 기준(각각 pass=true/false):
1. domain_fit — 구조가 요청한 용도/도메인에 실제로 적합한가
2. naming_quality — DB/속성/뷰 이름이 전문적인가 (generic "데이터베이스1/속성2" 류면 fail)
3. layout_sense — 블록/섹션 구성이 사용자 흐름상 합리적인가
4. completeness — 구매자가 "완성됐다"고 느낄 만한가 (빈 DB·누락 없이)
5. willingness_to_pay — 종합적으로 $20-49를 낼 만한가

반드시 아래 JSON만 출력하세요(설명·마크다운 금지):
{"verdicts":[{"criterion":"domain_fit","pass":true,"reason":"..."},...5개...],
 "overall_pass":true,"estimated_band":"$20-49"}"""


@dataclass
class JudgeVerdict:
    overall_pass: bool
    estimated_band: str
    verdicts: list[dict[str, Any]] = field(default_factory=list)
    pass_count: int = 0
    total: int = 0

    def to_metadata(self) -> dict[str, Any]:
        return {
            "judge_pass": self.overall_pass,
            "judge_band": self.estimated_band,
            "judge_pass_ratio": f"{self.pass_count}/{self.total}",
            "judge_fails": [v.get("criterion") for v in self.verdicts if not _truthy(v.get("pass"))],
        }


def _truthy(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.strip().lower() in ("true", "pass", "passed", "yes", "y", "1", "ok")
    if isinstance(v, (int, float)):
        return v >= 1
    return False


def _props(db: dict[str, Any]) -> dict[str, Any]:
    p = db.get("db_properties") or db.get("properties") or {}
    return p if isinstance(p, dict) else {}


def summarize_blueprint(blueprint: dict[str, Any], max_chars: int = 1800) -> str:
    """토큰 절약을 위해 블루프린트를 컴팩트 텍스트로 요약 (전체 덤프 금지)."""
    md = blueprint.get("metadata", {})
    lines = [f"제목: {md.get('title') or blueprint.get('main_page', {}).get('title', '?')}"]
    lines.append(f"용도(추정): {md.get('template_type', '?')}, 색상: {md.get('color_theme', '?')}")

    dbs = blueprint.get("databases", []) or []
    lines.append(f"\nDB {len(dbs)}개:")
    for i, db in enumerate(dbs):
        props = _props(db)
        prop_descr = []
        for name, spec in list(props.items())[:12]:
            t = spec if isinstance(spec, str) else (spec.get("type", "?") if isinstance(spec, dict) else "?")
            prop_descr.append(f"{name}:{t}")
        views = [v.get("type") if isinstance(v, dict) else v for v in db.get("views", [])]
        lines.append(
            f"  [{i}] {db.get('title', '?')} — 속성({len(props)}): {', '.join(prop_descr)}"
            f" | 뷰: {views} | 샘플 {len(db.get('sample_items', []))}행"
        )

    block_types = [b.get("type") for b in blueprint.get("blocks", []) if isinstance(b, dict)]
    lines.append(f"\n블록 흐름({len(block_types)}): {block_types[:20]}")

    subs = [sp.get("title") for sp in blueprint.get("sub_pages", []) if isinstance(sp, dict)]
    if subs:
        lines.append(f"하위 페이지: {subs}")

    text = "\n".join(lines)
    return text[:max_chars]


def _parse_verdict(result: Any) -> JudgeVerdict | None:
    if not isinstance(result, dict):
        return None
    raw_verdicts = result.get("verdicts")
    if not isinstance(raw_verdicts, list) or not raw_verdicts:
        return None
    verdicts = [v for v in raw_verdicts if isinstance(v, dict)]
    if not verdicts:
        return None
    pass_count = sum(1 for v in verdicts if _truthy(v.get("pass", v.get("passed"))))
    total = len(verdicts)
    if "overall_pass" in result:
        overall = _truthy(result["overall_pass"])
    else:
        overall = pass_count >= -(-total * 3 // 5)  # ceil(total*0.6)
    return JudgeVerdict(
        overall_pass=overall,
        estimated_band=str(result.get("estimated_band", "")),
        verdicts=verdicts,
        pass_count=pass_count,
        total=total,
    )


async def judge_blueprint(
    blueprint: dict[str, Any],
    ai_key: str = "",
    ai_model: str = "",
    provider: Any = None,
    timeout: float = 30.0,
) -> JudgeVerdict | None:
    """블루프린트를 LLM으로 주관적 심사. 실패/미설정/예산초과 시 None."""
    try:
        if provider is None:
            from app.agent.providers.router import ProviderRouter

            provider = ProviderRouter.resolve_with_fallback(api_key=ai_key, ai_model=ai_model)

        # 예산 초과면 judge는 조용히 스킵 (생성 결과는 이미 완성됨)
        try:
            from app.core.cost_control import note_call

            note_call()
        except Exception:
            return None

        summary = summarize_blueprint(blueprint)
        result = await provider.call_with_retry(JUDGE_SYSTEM_PROMPT, summary, model=ai_model, timeout=timeout)
        verdict = _parse_verdict(result)
        if verdict is None:
            logger.info("[PremiumJudge] verdict 파싱 실패 (provider 응답이 심사 형식 아님) — 스킵")
        return verdict
    except Exception as e:
        logger.info(f"[PremiumJudge 스킵] {str(e)[:100]}")
        return None
