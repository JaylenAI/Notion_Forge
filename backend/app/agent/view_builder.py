"""View configuration builder for Notion Views API.

AI blueprint의 view spec을 Notion Views API configuration 포맷으로 변환하는
독립 모듈. orchestrator.py에서 추출됨.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def build_view_configuration(view_spec: dict) -> dict | None:
    """AI blueprint의 view spec에서 Views API configuration 객체를 빌드.

    AI가 view spec에 넣은 세부 설정(cover, chart_type, date_property 등)을
    Notion Views API의 configuration 포맷으로 변환.
    설정이 없으면 None 반환 (기본값 사용).

    Args:
        view_spec: AI blueprint에서 생성된 뷰 설정 딕셔너리.
            최소한 ``{"type": "<view_type>"}`` 형태여야 한다.

    Returns:
        Notion Views API에 전달할 configuration dict, 또는 추가 설정이
        없으면 None.
    """
    vtype = view_spec.get("type", "table")
    config: dict[str, Any] = {"type": vtype}
    has_config = False

    logger.debug("view configuration 빌드 시작: type=%s", vtype)

    if vtype == "board":
        cover = view_spec.get("cover")
        if cover:
            config["cover"] = cover if isinstance(cover, dict) else {"type": cover}
            has_config = True
        cover_size = view_spec.get("cover_size")
        if cover_size:
            config["cover_size"] = cover_size
            has_config = True
        cover_aspect = view_spec.get("cover_aspect")
        if cover_aspect:
            config["cover_aspect"] = cover_aspect
            has_config = True
        card_layout = view_spec.get("card_layout")
        if card_layout:
            config["card_layout"] = card_layout
            has_config = True

    elif vtype == "gallery":
        cover = view_spec.get("cover")
        if cover:
            config["cover"] = cover if isinstance(cover, dict) else {"type": cover}
            has_config = True
        cover_size = view_spec.get("cover_size", "medium")
        if cover:
            config["cover_size"] = cover_size
            config["cover_aspect"] = view_spec.get("cover_aspect", "cover")
            has_config = True
        card_layout = view_spec.get("card_layout")
        if card_layout:
            config["card_layout"] = card_layout
            has_config = True

    elif vtype == "calendar":
        date_prop = view_spec.get("date_property") or view_spec.get("date_property_id")
        if date_prop:
            config["date_property_id"] = date_prop
            has_config = True
        show_weekends = view_spec.get("show_weekends")
        if show_weekends is not None:
            config["show_weekends"] = show_weekends
            has_config = True

    elif vtype == "chart":
        chart_type = view_spec.get("chart_type")
        if chart_type:
            config["chart_type"] = chart_type
            has_config = True
        x_axis = view_spec.get("x_axis")
        if x_axis:
            config["x_axis"] = x_axis
            has_config = True
        y_axis = view_spec.get("y_axis")
        if y_axis:
            config["y_axis"] = y_axis
            has_config = True
        color_theme = view_spec.get("color_theme")
        if color_theme:
            config["color_theme"] = color_theme
            has_config = True
        if view_spec.get("show_data_labels") is not None:
            config["show_data_labels"] = view_spec["show_data_labels"]
            has_config = True
        height = view_spec.get("height")
        if height:
            config["height"] = height
            has_config = True

    elif vtype == "timeline":
        date_prop = view_spec.get("date_property") or view_spec.get("date_property_id")
        if date_prop:
            config["date_property_id"] = date_prop
            has_config = True
        end_date = view_spec.get("end_date_property_id")
        if end_date:
            config["end_date_property_id"] = end_date
            has_config = True
        arrows_by = view_spec.get("arrows_by")
        if arrows_by:
            config["arrows_by"] = arrows_by
            has_config = True
        zoom = view_spec.get("zoom_level")
        if zoom:
            config["preference"] = {"zoom_level": zoom}
            has_config = True

    elif vtype == "table":
        wrap_cells = view_spec.get("wrap_cells")
        if wrap_cells is not None:
            config["wrap_cells"] = wrap_cells
            has_config = True
        frozen = view_spec.get("frozen_column_index")
        if frozen is not None:
            config["frozen_column_index"] = frozen
            has_config = True

    elif vtype == "map":
        map_by = view_spec.get("map_by")
        if map_by:
            config["map_by"] = map_by
            has_config = True
        height = view_spec.get("height")
        if height:
            config["height"] = height
            has_config = True

    elif vtype == "form":
        if view_spec.get("anonymous_submissions") is not None:
            config["anonymous_submissions"] = view_spec["anonymous_submissions"]
            has_config = True
        permissions = view_spec.get("submission_permissions")
        if permissions:
            config["submission_permissions"] = permissions
            has_config = True

    if has_config:
        logger.debug("view configuration 빌드 완료: %s", config)
    else:
        logger.debug("추가 설정 없음, None 반환 (type=%s)", vtype)

    return config if has_config else None
