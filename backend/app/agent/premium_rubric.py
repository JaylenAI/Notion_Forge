"""PremiumRubric: 마켓플레이스 '유료급' 결정적 품질 루브릭 (Phase A1).

QualityValidator(구조 무결성)와 별개로, "이 템플릿이 실제로 팔릴 수준인가"를
0~100점으로 채점한다. 시장 리서치(2026-06)에서 도출한 10개 기준 중
**블루프린트에서 계산 가능한** 항목만 결정적으로 채점하고, 산출물에 담을 수 없는
항목(영상 튜토리얼·업데이트/지원)은 applicable=False로 정규화에서 제외한다.

가격 밴드(리서치 가격 절벽):
  <40 판매불가 · 40~59 $5-15 · 60~74 $20-49 · 75~89 $50-99 · 90+ 플래그십

주관적 품질(도메인 적합성·네이밍 센스 등)은 premium_judge(LLM)가 담당한다.
"""

from dataclasses import dataclass, field
from typing import Any

# 가이드/온보딩 페이지 탐지용 키워드
_GUIDE_WORDS = (
    "시작",
    "사용법",
    "사용 방법",
    "가이드",
    "안내",
    "설명서",
    "튜토리얼",
    "온보딩",
    "읽어",
    "getting started",
    "how to",
    "how-to",
    "start here",
    "guide",
    "instruction",
)


@dataclass
class CriterionScore:
    key: str
    label: str
    weight: int
    score: float  # 0.0 ~ 1.0
    applicable: bool = True
    note: str = ""


@dataclass
class PremiumRubricResult:
    score: float  # 0~100 (적용 가능 항목으로 정규화)
    band_label: str
    band_price: str
    criteria: list[CriterionScore] = field(default_factory=list)

    def weakest(self, n: int = 3) -> list[CriterionScore]:
        """개선 우선순위 — 적용 가능 항목 중 (가중치 × 결손)이 큰 순."""
        applicable = [c for c in self.criteria if c.applicable]
        return sorted(applicable, key=lambda c: c.weight * (1.0 - c.score), reverse=True)[:n]

    def to_metadata(self) -> dict[str, Any]:
        return {
            "premium_score": round(self.score, 1),
            "premium_band": self.band_price,
            "premium_band_label": self.band_label,
            "premium_weakest": [c.key for c in self.weakest(3)],
        }


# ── 유틸 ────────────────────────────────────────────────────


def _props(db: dict[str, Any]) -> dict[str, Any]:
    p = db.get("db_properties") or db.get("properties") or {}
    return p if isinstance(p, dict) else {}


def _ptype(pspec: Any) -> str:
    if isinstance(pspec, str):
        return pspec
    if isinstance(pspec, dict):
        return pspec.get("type", "")
    return ""


def _count_prop_type(databases: list[dict[str, Any]], ptype: str) -> int:
    return sum(1 for db in databases for spec in _props(db).values() if _ptype(spec) == ptype)


def _block_types(blocks: list[Any]) -> list[str]:
    return [b.get("type") for b in blocks if isinstance(b, dict)]


def _text_blob(blueprint: dict[str, Any]) -> str:
    """온보딩 탐지를 위해 블록/서브페이지 제목·텍스트를 소문자로 모은다."""
    parts: list[str] = []
    for b in blueprint.get("blocks", []):
        if isinstance(b, dict):
            parts.append(str(b.get("text", "")))
            parts.append(str(b.get("children_text", "")))
    for sp in blueprint.get("sub_pages", []):
        if isinstance(sp, dict):
            parts.append(str(sp.get("title", "")))
            parts.append(str(sp.get("description", "")))
    return " ".join(parts).lower()


# ── 개별 기준 채점 (각 0.0~1.0) ─────────────────────────────


def _score_linked_db(databases: list[dict[str, Any]]) -> tuple[float, str]:
    n = len(databases)
    relations = _count_prop_type(databases, "relation")
    if n == 0:
        return 0.0, "DB 없음"
    base = {1: 0.35}.get(n, 0.65 if n == 2 else 0.9)
    if relations >= 1 and n >= 2:
        base = min(1.0, base + 0.1)
    return base, f"DB {n}개, relation {relations}개"


def _score_relation_rollup(databases: list[dict[str, Any]]) -> tuple[float, str]:
    relations = _count_prop_type(databases, "relation")
    rollups = _count_prop_type(databases, "rollup")
    if relations == 0:
        return (0.1 if rollups else 0.0), "relation 없음 (집계 불가)"
    score = 0.5
    if rollups >= 1:
        score += 0.3
    # 샘플행이 relation을 실제로 채우는지 — 채워야 rollup이 집계됨
    linked = False
    for db in databases:
        rel_names = [name for name, spec in _props(db).items() if _ptype(spec) == "relation"]
        for item in db.get("sample_items", []):
            if isinstance(item, dict) and any(item.get(rn) for rn in rel_names):
                linked = True
                break
        if linked:
            break
    if linked:
        score += 0.2
    return min(1.0, score), f"relation {relations}/rollup {rollups}/샘플링크 {'O' if linked else 'X'}"


def _score_dashboard(blocks: list[Any]) -> tuple[float, str]:
    types = _block_types(blocks)
    db_refs = types.count("database_ref") + types.count("linked_view")
    has_columns = "column_list" in types
    if db_refs == 0:
        return 0.1, "DB 임베드 없음"
    score = 0.5 if db_refs == 1 else 0.75
    if has_columns:
        score += 0.25
    return min(1.0, score), f"db_ref {db_refs}개, 컬럼레이아웃 {'O' if has_columns else 'X'}"


def _score_formula(databases: list[dict[str, Any]]) -> tuple[float, str]:
    formulas = _count_prop_type(databases, "formula")
    # 버튼/자동화는 Notion API로 생성 불가 → 이 기준 상한 0.9, 미감점
    if formulas == 0:
        return 0.2, "formula 없음 (버튼/자동화는 API 한계)"
    return (0.7 if formulas == 1 else 0.9), f"formula {formulas}개"


def _score_onboarding(blueprint: dict[str, Any]) -> tuple[float, str]:
    # 1) 전용 가이드 서브페이지
    for sp in blueprint.get("sub_pages", []):
        if isinstance(sp, dict) and any(w in str(sp.get("title", "")).lower() for w in _GUIDE_WORDS):
            return 1.0, "전용 가이드 서브페이지"
    # 2) 본문에 가이드 섹션
    if any(w in _text_blob(blueprint) for w in _GUIDE_WORDS):
        return 0.7, "본문 가이드 섹션"
    # 3) 환영 callout만
    if blueprint.get("blocks") and _block_types(blueprint["blocks"])[:1] == ["callout"]:
        return 0.3, "환영 callout만 (전용 안내 없음)"
    return 0.0, "온보딩 없음"


def _score_visual(blueprint: dict[str, Any]) -> tuple[float, str]:
    score = 0.0
    main = blueprint.get("main_page", {})
    if main.get("cover_url"):
        score += 0.3
    if main.get("icon"):
        score += 0.2
    subs = [sp for sp in blueprint.get("sub_pages", []) if isinstance(sp, dict)]
    if subs and all(sp.get("icon") for sp in subs):
        score += 0.2
    if any(db.get("icon") for db in blueprint.get("databases", [])):
        score += 0.1
    if blueprint.get("metadata", {}).get("color_theme", "default") != "default":
        score += 0.2
    return min(1.0, score), "커버/아이콘/테마 적용도"


def _score_sample_data(databases: list[dict[str, Any]]) -> tuple[float, str]:
    if not databases:
        return 0.0, "DB 없음"
    counts = [len(db.get("sample_items", [])) for db in databases]
    avg = sum(counts) / len(counts)
    if avg < 1:
        return 0.0, "샘플 데이터 없음"
    if avg >= 5:
        return 1.0, f"평균 {avg:.1f}행"
    if avg >= 3:
        return 0.7, f"평균 {avg:.1f}행"
    return 0.4, f"평균 {avg:.1f}행 (3+ 권장)"


def _score_mobile_nav(blocks: list[Any]) -> tuple[float, str]:
    # 정밀 모바일 검증은 A2(상단 네비 기본화)/렌더 단계. 여기선 네비 구조 유무만 근사.
    types = _block_types(blocks)
    nav_signal = "table_of_contents" in types or any(
        isinstance(b, dict) and b.get("type") == "column_list" and _has_page_links(b) for b in blocks
    )
    return (0.8, "네비 구조 감지") if nav_signal else (0.4, "명시적 네비 없음 (A2에서 상단네비 기본화)")


def _has_page_links(column_block: dict[str, Any]) -> bool:
    for col in column_block.get("columns", []):
        if isinstance(col, list):
            for item in col:
                if isinstance(item, dict) and (item.get("type") == "link_to_page" or item.get("sub_page_ref")):
                    return True
    return False


def _band(score: float) -> tuple[str, str]:
    if score < 40:
        return "판매 불가", "$0"
    if score < 60:
        return "심플", "$5-15"
    if score < 75:
        return "멀티DB 시스템", "$20-49"
    if score < 90:
        return "프리미엄", "$50-99"
    return "플래그십", "$100+"


# ── 메인 채점기 ─────────────────────────────────────────────


def score_blueprint(blueprint: dict[str, Any]) -> PremiumRubricResult:
    """블루프린트를 0~100 유료급 루브릭으로 결정적 채점."""
    databases = blueprint.get("databases", []) or []
    blocks = blueprint.get("blocks", []) or []

    specs: list[tuple[str, str, int, tuple[float, str], bool]] = [
        ("linked_db", "연결된 DB 아키텍처", 18, _score_linked_db(databases), True),
        ("relation_rollup", "작동하는 relation+rollup", 15, _score_relation_rollup(databases), True),
        ("dashboard", "대시보드/허브", 12, _score_dashboard(blocks), True),
        ("formula", "formula·자동화", 10, _score_formula(databases), True),
        ("onboarding", "온보딩/시작하기", 12, _score_onboarding(blueprint), True),
        ("visual", "시각(아이콘/커버/테마)", 10, _score_visual(blueprint), True),
        ("sample_data", "샘플 데이터", 7, _score_sample_data(databases), True),
        ("mobile_nav", "모바일/네비", 6, _score_mobile_nav(blocks), True),
        ("video", "영상/튜토리얼", 6, (0.0, "산출물 밖 — 제작자 몫"), False),
        ("support", "업데이트/지원", 4, (0.0, "산출물 밖 — 제작자 몫"), False),
    ]

    criteria = [
        CriterionScore(key=k, label=lbl, weight=w, score=round(sc[0], 3), applicable=ap, note=sc[1])
        for (k, lbl, w, sc, ap) in specs
    ]

    applicable_weight = sum(c.weight for c in criteria if c.applicable)
    earned = sum(c.weight * c.score for c in criteria if c.applicable)
    total = (earned / applicable_weight * 100.0) if applicable_weight else 0.0
    label, price = _band(total)

    return PremiumRubricResult(score=round(total, 1), band_label=label, band_price=price, criteria=criteria)
