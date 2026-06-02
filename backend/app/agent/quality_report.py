"""QualityReport: 구조 검증 + 유료급 루브릭 + LLM 심사 통합 (Phase A1).

3개 신호를 하나의 리포트로 묶고, 블루프린트 metadata에 부착한다:
  1. QualityValidator   — 구조 무결성 (schema/content/design)  [기존]
  2. premium_rubric     — 유료급 결정적 점수 0~100 + 가격 밴드   [신규]
  3. premium_judge      — 주관적 품질 LLM PASS/FAIL              [신규, 선택]

A1에서는 **비차단**(측정만). 차단 게이트는 A4에서 활성화한다.
"""

import logging
from dataclasses import dataclass
from typing import Any

from app.agent.premium_judge import JudgeVerdict, judge_blueprint
from app.agent.premium_rubric import PremiumRubricResult, score_blueprint

logger = logging.getLogger("notionforge.quality_report")


@dataclass
class QualityReport:
    structural_score: float
    structural_passed: bool
    premium: PremiumRubricResult
    judge: JudgeVerdict | None = None
    structural_breakdown: dict[str, float] | None = None

    def to_metadata(self) -> dict[str, Any]:
        md: dict[str, Any] = {
            "quality_score": self.structural_score,
            "quality_passed": self.structural_passed,
        }
        if self.structural_breakdown is not None:
            md["quality_breakdown"] = self.structural_breakdown
        md.update(self.premium.to_metadata())
        if self.judge is not None:
            md.update(self.judge.to_metadata())
        return md


def build_deterministic_report(blueprint: dict[str, Any]) -> QualityReport:
    """LLM 없이 결정적 신호만 (구조 + 유료급 루브릭). QualityValidator는 1회만 실행."""
    from app.agent.quality_validator import QualityValidator

    structural = QualityValidator().validate(blueprint)
    premium = score_blueprint(blueprint)
    return QualityReport(
        structural_score=structural.score,
        structural_passed=structural.passed,
        premium=premium,
        structural_breakdown=structural.layer_scores,
    )


def attach_deterministic_quality(blueprint: dict[str, Any]) -> QualityReport:
    """결정적 품질 신호를 계산해 blueprint['metadata']에 부착 (비차단)."""
    report = build_deterministic_report(blueprint)
    md = blueprint.setdefault("metadata", {})
    md.update(report.to_metadata())
    logger.info(
        f"[QualityReport] 구조={report.structural_score:.0f} "
        f"유료급={report.premium.score:.0f} ({report.premium.band_price}) "
        f"최약점={[c.key for c in report.premium.weakest(3)]}"
    )
    return report


async def attach_full_quality(
    blueprint: dict[str, Any],
    ai_key: str = "",
    ai_model: str = "",
    enable_judge: bool = True,
    provider: Any = None,
) -> QualityReport:
    """결정적 신호 + (선택)LLM 심사까지 부착. 심사 실패 시 결정적 신호만."""
    report = attach_deterministic_quality(blueprint)
    if enable_judge:
        verdict = await judge_blueprint(blueprint, ai_key=ai_key, ai_model=ai_model, provider=provider)
        if verdict is not None:
            report.judge = verdict
            blueprint.setdefault("metadata", {}).update(verdict.to_metadata())
            logger.info(
                f"[QualityReport] LLM심사 overall={'PASS' if verdict.overall_pass else 'FAIL'} "
                f"({verdict.pass_count}/{verdict.total}) band={verdict.estimated_band}"
            )
    return report
