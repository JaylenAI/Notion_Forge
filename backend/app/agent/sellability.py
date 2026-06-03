"""Sellability: 유료급 셀러빌리티 보강 (Phase A2).

구매자 환불 트리거(리서치)를 직접 해소하는 결정적 보강을 조립된 blueprint에 주입한다:
  1. 온보딩 "시작하기" 페이지 — 구매자 불만 1위(빈 DB·안내 없음) 해소, 템플릿 인지형
  2. 상단 네비 — 모바일 좌측 사이드바 스크롤 문제 해소(상단 가로 네비)
  3. 목차(table_of_contents) — 본문 내 이동성

모두 **멱등**(이미 있으면 스킵)하며 Notion API로 생성 가능한 블록만 사용한다.
리스팅 키트(판매 보조)는 listing_kit 모듈이 담당.
"""

from typing import Any

from app.agent.premium_rubric import _GUIDE_WORDS

_NAV_MAX = 5  # 상단 네비에 노출할 최대 하위 페이지 수


def _bg(blueprint: dict[str, Any]) -> str:
    color = blueprint.get("metadata", {}).get("color_theme", "default")
    return f"{color}_background" if color and color != "default" else "default"


def _has_guide_subpage(blueprint: dict[str, Any]) -> bool:
    for sp in blueprint.get("sub_pages", []):
        if isinstance(sp, dict) and any(w in str(sp.get("title", "")).lower() for w in _GUIDE_WORDS):
            return True
    return False


def _db_lines(blueprint: dict[str, Any]) -> list[str]:
    """온보딩 '구성' 섹션용 — 실제 DB명/설명으로 템플릿 인지형 안내."""
    lines: list[str] = []
    for db in blueprint.get("databases", []):
        title = db.get("title", "데이터베이스")
        desc = db.get("description", "")
        props = db.get("db_properties") or db.get("properties") or {}
        views = [v.get("type") if isinstance(v, dict) else v for v in db.get("views", [])]
        view_str = f" · 뷰: {', '.join(str(v) for v in views)}" if views else ""
        lines.append(f"**{title}** — {desc or f'속성 {len(props)}개'}{view_str}")
    return lines


def _build_onboarding_subpage(blueprint: dict[str, Any]) -> dict[str, Any]:
    """템플릿 구조를 반영한 '시작하기' 가이드 페이지 블록 구성."""
    bg = _bg(blueprint)
    title = blueprint.get("metadata", {}).get("title", "이 템플릿")
    blocks: list[dict[str, Any]] = [
        {
            "type": "callout",
            "text": f"{title} 사용을 환영합니다! 이 페이지는 템플릿 구성과 사용법을 안내합니다.",
            "icon": "👋",
            "color": bg,
        },
        {"type": "heading_2", "text": "📦 구성", "color": bg},
    ]
    db_lines = _db_lines(blueprint)
    if db_lines:
        blocks += [{"type": "bulleted_list_item", "text": line} for line in db_lines]
    else:
        blocks.append({"type": "paragraph", "text": "본문의 데이터베이스에 항목을 추가해 사용하세요."})

    blocks += [
        {"type": "heading_2", "text": "🚀 사용 방법", "color": bg},
        {"type": "numbered_list_item", "text": "각 데이터베이스의 '+ 새로 만들기'로 항목을 추가하세요."},
        {"type": "numbered_list_item", "text": "보드·캘린더 등 뷰 탭을 전환해 상태/일정 기준으로 확인하세요."},
        {"type": "numbered_list_item", "text": "연결(relation)·집계(rollup)·수식(formula) 속성은 자동으로 계산됩니다."},
        {"type": "heading_2", "text": "🎨 맞춤 설정", "color": bg},
        {"type": "bulleted_list_item", "text": "페이지 색상·아이콘·커버는 자유롭게 바꿀 수 있습니다."},
        {"type": "bulleted_list_item", "text": "필요한 속성을 추가하거나 불필요한 속성을 삭제하세요."},
        {"type": "heading_2", "text": "🧹 샘플 데이터 정리", "color": bg},
        {
            "type": "paragraph",
            "text": "미리 채워진 샘플 행은 사용 예시입니다. 익숙해지면 삭제하고 실제 데이터를 입력하세요.",
        },
    ]
    return {"title": "🚀 시작하기", "icon": "🚀", "blocks": blocks}


def inject_onboarding_page(blueprint: dict[str, Any]) -> bool:
    """'시작하기' 가이드 페이지를 sub_pages에 주입 (이미 있으면 스킵). 주입 여부 반환."""
    if _has_guide_subpage(blueprint):
        return False
    blueprint.setdefault("sub_pages", []).append(_build_onboarding_subpage(blueprint))
    return True


def _nav_already_present(blocks: list[Any]) -> bool:
    """상단부에 페이지 링크 네비(column_list of link_to_page)가 이미 있는지."""
    for b in blocks[:4]:
        if not isinstance(b, dict):
            continue
        if b.get("type") == "column_list":
            for col in b.get("columns", []):
                items = col if isinstance(col, list) else col.get("blocks", []) if isinstance(col, dict) else []
                if any(isinstance(it, dict) and it.get("type") == "link_to_page" for it in items):
                    return True
        if b.get("type") == "link_to_page":
            return True
    return False


def inject_top_nav(blueprint: dict[str, Any]) -> bool:
    """하위 페이지로 가는 상단 네비를 주입 (모바일 친화 가로 네비). 주입 여부 반환."""
    blocks = blueprint.setdefault("blocks", [])
    titles = [sp.get("title") for sp in blueprint.get("sub_pages", []) if isinstance(sp, dict) and sp.get("title")]
    titles = titles[:_NAV_MAX]
    # 적응형: 링크 대상 하위 페이지가 2개 이상일 때만 가로 네비를 만든다.
    # (단일 페이지 네비는 의미 없는 클러터 — 모든 템플릿이 같은 셸로 보이던 원인 중 하나)
    if len(titles) < 2 or _nav_already_present(blocks):
        return False

    nav_block: dict[str, Any] = {
        "type": "column_list",
        "columns": [[{"type": "link_to_page", "sub_page_ref": t}] for t in titles],
    }

    # 환영 callout 다음(있으면)에 네비 삽입
    insert_at = 1 if blocks and isinstance(blocks[0], dict) and blocks[0].get("type") == "callout" else 0
    blocks.insert(insert_at, nav_block)
    return True


def ensure_toc(blueprint: dict[str, Any]) -> bool:
    """본문에 목차가 없고 heading이 있으면 목차 1개 주입. 주입 여부 반환."""
    blocks = blueprint.setdefault("blocks", [])
    types = [b.get("type") for b in blocks if isinstance(b, dict)]
    if "table_of_contents" in types:
        return False
    # 적응형: 섹션이 충분히 많을 때(heading ≥3)만 목차를 넣는다. 짧은 단순 템플릿엔 불필요.
    if sum(1 for t in types if t in ("heading_1", "heading_2")) < 3:
        return False
    insert_at = 1 if blocks and isinstance(blocks[0], dict) and blocks[0].get("type") == "callout" else 0
    blocks.insert(insert_at, {"type": "table_of_contents", "color": "default"})
    return True


def enrich_blueprint(blueprint: dict[str, Any]) -> dict[str, bool]:
    """조립된 blueprint에 셀러빌리티 보강을 적용. 적용 내역 반환.

    순서 중요: 온보딩 페이지를 먼저 추가해야 상단 네비가 그 페이지도 링크한다.

    적응형 — 단일 DB의 단순 트래커엔 별도 온보딩 페이지를 강제하지 않는다(self-evident).
    멀티 DB의 복잡한 템플릿에만 풍부한 셸을 적용해, 템플릿 복잡도에 따라 형태가 달라지게 한다.
    (모든 템플릿에 동일 셸을 박아 다양성을 가리던 회귀 수정.)
    """
    multi_db = len(blueprint.get("databases", [])) >= 2
    onboarding = inject_onboarding_page(blueprint) if multi_db else False
    toc = ensure_toc(blueprint)
    nav = inject_top_nav(blueprint)
    applied = {"onboarding": onboarding, "top_nav": nav, "toc": toc}
    blueprint.setdefault("metadata", {})["sellability_applied"] = [k for k, v in applied.items() if v]
    return applied
