"""ListingKit: 마켓플레이스 판매 보조 자료 생성 (Phase A2).

조립된 blueprint 구조에서 **결정적으로** 리스팅 키트를 생성한다(LLM 불필요):
제목·태그라인·설명·기능 불릿·≤60초 프리뷰 스크립트·추천 가격밴드.

발행(Notion Site + duplicate-as-template)은 UI 전용이라 자동화 불가 — 이 키트는
판매자가 등록 시 바로 쓸 수 있는 초안을 제공한다.
"""

from typing import Any

from app.agent.premium_rubric import _ptype, score_blueprint


def _props(db: dict[str, Any]) -> dict[str, Any]:
    p = db.get("db_properties") or db.get("properties") or {}
    return p if isinstance(p, dict) else {}


def _collect(blueprint: dict[str, Any]) -> dict[str, Any]:
    dbs = blueprint.get("databases", []) or []
    view_types: set[str] = set()
    relations = rollups = formulas = 0
    samples = 0
    for db in dbs:
        for v in db.get("views", []):
            vt = v.get("type") if isinstance(v, dict) else v
            if vt:
                view_types.add(str(vt))
        for spec in _props(db).values():
            t = _ptype(spec)
            relations += t == "relation"
            rollups += t == "rollup"
            formulas += t == "formula"
        samples += len(db.get("sample_items", []))
    return {
        "db_count": len(dbs),
        "db_titles": [db.get("title", "DB") for db in dbs],
        "view_types": sorted(view_types),
        "relations": relations,
        "rollups": rollups,
        "formulas": formulas,
        "samples": samples,
        "sub_pages": len(blueprint.get("sub_pages", []) or []),
    }


def _features(s: dict[str, Any]) -> list[str]:
    feats: list[str] = []
    if s["db_count"] >= 2:
        feats.append(f"{s['db_count']}개 연결 데이터베이스: {', '.join(s['db_titles'][:5])}")
    elif s["db_count"] == 1:
        feats.append(f"핵심 데이터베이스: {s['db_titles'][0]}")
    if s["relations"]:
        feats.append(f"데이터베이스 간 연결(relation) {s['relations']}개")
    if s["rollups"]:
        feats.append(f"자동 집계(rollup) {s['rollups']}개 — 합계·개수·평균 자동 계산")
    if s["formulas"]:
        feats.append(f"수식(formula) {s['formulas']}개 — D-Day·진행률 등 자동 계산")
    if s["view_types"]:
        feats.append(f"다중 뷰: {', '.join(s['view_types'])}")
    if s["samples"]:
        feats.append(f"바로 쓰는 샘플 데이터 {s['samples']}행 (정리 가능)")
    feats.append("시작하기 가이드 페이지 포함")
    return feats


def _preview_script(title: str, s: dict[str, Any]) -> list[str]:
    script = [f"0:00 — '{title}' 메인 대시보드 한눈에 보기"]
    if s["sub_pages"]:
        script.append("0:08 — 상단 네비로 '시작하기' 가이드 이동")
    if s["db_titles"]:
        script.append(f"0:18 — '{s['db_titles'][0]}'에 항목 추가 시연")
    if s["view_types"]:
        script.append(f"0:32 — 뷰 전환({', '.join(s['view_types'][:3])})")
    if s["rollups"] or s["formulas"]:
        script.append("0:45 — 연결·자동 집계/수식이 실시간 갱신되는 모습")
    script.append("0:55 — 복제 후 바로 사용 가능 안내로 마무리")
    return script


def build_listing_kit(blueprint: dict[str, Any]) -> dict[str, Any]:
    """blueprint 구조 기반 마켓플레이스 리스팅 키트 초안 생성."""
    title = blueprint.get("metadata", {}).get("title") or blueprint.get("main_page", {}).get("title", "Notion 템플릿")
    s = _collect(blueprint)
    rubric = score_blueprint(blueprint)

    if s["db_count"] >= 2:
        tagline = f"{', '.join(s['db_titles'][:3])}를 한 곳에서 연결·관리하는 올인원 시스템"
    elif s["db_count"] == 1:
        tagline = f"{s['db_titles'][0]} 관리를 깔끔하게 — 바로 쓰는 템플릿"
    else:
        tagline = "바로 쓰는 Notion 템플릿"

    features = _features(s)
    description = (
        f"{title}은(는) {tagline}. "
        + (f"{s['db_count']}개의 데이터베이스" if s["db_count"] else "구조화된 페이지")
        + ("가 relation·rollup으로 연결되어 자동 집계되며, " if s["relations"] else "로 구성되며, ")
        + "샘플 데이터와 시작하기 가이드가 포함되어 복제 즉시 사용할 수 있습니다."
    )

    return {
        "title": title,
        "tagline": tagline,
        "description": description,
        "features": features,
        "preview_script": _preview_script(title, s),
        "suggested_price_band": rubric.band_price,
        "quality_score": rubric.score,
    }
