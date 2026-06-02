"""VisualEnrich: 시각 프리미엄 보강 (Phase A3).

조립된 blueprint에 결정적 시각/뷰 보강을 적용한다(모두 멱등):
  1. 뷰 큐레이션 — DB 속성에 맞춰 board(상태/선택별)·calendar(날짜) 자동 추가.
     view_ops 클라이언트(244줄, 10종 뷰)는 이미 완비 → 생성기가 안 만들던 풍부한
     뷰를 골든이 쓰는 **검증된 포맷**으로 채운다(creation_executor가 date_property 이름→ID 해결).
  2. 아이콘 보강 — 메인/DB/하위페이지에 의미 있는 기본 아이콘 보장(루브릭 시각 항목 ↑).

커스텀 업로드 커버(파일 업로드 API)는 이미지 소스(생성 모델) 필요 → 후속.
여기선 카테고리 인지형 아이콘으로 시각 변별을 높인다.
"""

from typing import Any

from app.agent.premium_rubric import _ptype

# 제목 키워드 → 의미 아이콘 (부분일치, 위에서부터 우선)
_ICON_KEYWORDS: list[tuple[tuple[str, ...], str]] = [
    (("고객", "client", "customer", "crm", "연락처", "contact"), "👥"),
    (("딜", "거래", "매출", "sales", "deal", "수익", "재무", "finance", "예산", "가계"), "💰"),
    (("프로젝트", "project"), "📁"),
    (("작업", "task", "할일", "todo", "투두"), "✅"),
    (("일정", "캘린더", "calendar", "schedule", "event", "이벤트"), "📅"),
    (("독서", "책", "book", "read"), "📚"),
    (("운동", "헬스", "workout", "fitness", "건강", "health"), "💪"),
    (("습관", "habit", "루틴", "routine"), "🔁"),
    (("노트", "메모", "note", "지식", "위키", "wiki"), "📝"),
    (("목표", "goal", "okr", "kpi"), "🎯"),
    (("콘텐츠", "content", "블로그", "blog", "영상", "video"), "🎬"),
    (("회의", "meeting", "팀", "team"), "🤝"),
    (("재고", "상품", "product", "inventory", "주문", "order"), "📦"),
]
_DEFAULT_DB_ICON = "🗂️"


def _props(db: dict[str, Any]) -> dict[str, Any]:
    p = db.get("db_properties") or db.get("properties") or {}
    return p if isinstance(p, dict) else {}


def _icon_for(title: str) -> str:
    t = (title or "").lower()
    for keywords, icon in _ICON_KEYWORDS:
        if any(k in t for k in keywords):
            return icon
    return _DEFAULT_DB_ICON


def _view_types(views: list[Any]) -> set[str]:
    out: set[str] = set()
    for v in views:
        if isinstance(v, dict) and v.get("type"):
            out.add(v["type"])
        elif isinstance(v, str):
            out.add(v)
    return out


def _first_prop_of_type(props: dict[str, Any], *types: str) -> str | None:
    for name, spec in props.items():
        if _ptype(spec) in types:
            return name
    return None


def curate_views(blueprint: dict[str, Any], max_views: int = 4) -> int:
    """각 DB에 속성 기반 뷰를 보강(멱등). 추가한 뷰 총수 반환.

    - 항상 table 보장
    - status/select 속성 → board(그룹: 해당 속성)
    - date 속성 → calendar
    검증된 골든 포맷으로 추가하므로 creation_executor가 그대로 생성한다.
    """
    added = 0
    for db in blueprint.get("databases", []):
        props = _props(db)
        views = db.setdefault("views", [])
        # 문자열 뷰를 dict로 정규화 (일관 처리)
        norm = [{"type": v} if isinstance(v, str) else v for v in views if isinstance(v, (str, dict))]
        present = _view_types(norm)

        if "table" not in present:
            norm.append({"type": "table", "title": "전체"})
            present.add("table")
            added += 1

        group_prop = _first_prop_of_type(props, "status", "select")
        if group_prop and "board" not in present and len(norm) < max_views:
            norm.append({"type": "board", "title": f"{group_prop}별", "group_by": {"property": group_prop}})
            present.add("board")
            added += 1

        date_prop = _first_prop_of_type(props, "date")
        if date_prop and not ({"calendar", "timeline"} & present) and len(norm) < max_views:
            norm.append({"type": "calendar", "title": "캘린더", "date_property": date_prop})
            present.add("calendar")
            added += 1

        db["views"] = norm[:max_views]
    return added


def ensure_icons(blueprint: dict[str, Any]) -> int:
    """메인/DB/하위페이지에 의미 있는 기본 아이콘 보장(멱등). 채운 개수 반환."""
    filled = 0
    main = blueprint.setdefault("main_page", {})
    if not main.get("icon"):
        main["icon"] = _icon_for(main.get("title", "") or blueprint.get("metadata", {}).get("title", ""))
        filled += 1

    for db in blueprint.get("databases", []):
        if isinstance(db, dict) and not db.get("icon"):
            db["icon"] = _icon_for(db.get("title", ""))
            filled += 1

    for sp in blueprint.get("sub_pages", []):
        if isinstance(sp, dict) and not sp.get("icon"):
            sp["icon"] = _icon_for(sp.get("title", ""))
            filled += 1
    return filled


def enrich_visuals(blueprint: dict[str, Any]) -> dict[str, int]:
    """시각 보강 적용(뷰 큐레이션 + 아이콘). 적용 내역 반환."""
    views_added = curate_views(blueprint)
    icons_filled = ensure_icons(blueprint)
    result = {"views_added": views_added, "icons_filled": icons_filled}
    blueprint.setdefault("metadata", {})["visual_enriched"] = result
    return result
