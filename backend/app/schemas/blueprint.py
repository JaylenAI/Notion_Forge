from typing import Any

from pydantic import BaseModel, Field


class IntentResult(BaseModel):
    intent: str  # CREATE | MODIFY | QUESTION | CONFIRM | REJECT
    template_type: str  # dashboard | tracker | bookmark | ...
    title: str | None = None
    color_theme: str = "default"
    databases: list[dict] | None = None
    sub_pages: list[str] | None = None
    missing_info: list[str] | None = None
    confidence: float = 0.0
    modify_type: str | None = None


# ── Blueprint 타입 정의 (Phase 11) ──────────────────────────


class BlockSpec(BaseModel):
    """블록 스펙 — AI가 생성하는 블록 구조"""

    type: str  # callout, heading_1, heading_2, paragraph, toggle, database_ref, ...
    text: str = ""
    icon: str = ""
    color: str = ""
    children: list["BlockSpec"] = Field(default_factory=list)
    children_text: str = ""
    # database_ref 전용
    db_index: int = 0
    # link_to_page 전용
    page_id: str = ""
    sub_page_ref: str = ""
    # linked_view 전용
    view_type: str = ""
    filter: dict[str, Any] | None = None
    # column_list 전용
    columns: list[Any] = Field(default_factory=list)
    width_ratios: list[float] | None = None

    model_config = {"extra": "allow"}


class ViewSpec(BaseModel):
    """DB 뷰 스펙"""

    type: str = "table"  # table, board, gallery, calendar, timeline, chart, list, map, form
    title: str = ""
    filters: dict[str, Any] | None = None
    sorts: list[dict[str, Any]] | None = None
    group_by: dict[str, Any] | None = None
    configuration: dict[str, Any] | None = None

    model_config = {"extra": "allow"}


class DatabaseSpec(BaseModel):
    """데이터베이스 스펙"""

    title: str
    properties: dict[str, Any] = Field(default_factory=dict)
    db_properties: dict[str, Any] = Field(default_factory=dict)
    views: list[ViewSpec | dict | str] = Field(default_factory=list)
    sample_items: list[dict[str, Any]] = Field(default_factory=list)
    is_inline: bool = True
    description: str = ""
    icon: str = ""
    cover_url: str = ""
    db_parent: str = ""

    model_config = {"extra": "allow"}


class MainPageSpec(BaseModel):
    """메인 페이지 스펙"""

    title: str
    icon: str = ""
    cover_url: str = ""

    model_config = {"extra": "allow"}


class SubPageSpec(BaseModel):
    """하위 페이지 스펙"""

    title: str
    icon: str = ""
    description: str = ""
    blocks: list[dict[str, Any]] = Field(default_factory=list)

    model_config = {"extra": "allow"}


class BlueprintMetadata(BaseModel):
    """블루프린트 메타데이터"""

    title: str = ""
    template_type: str = ""
    color_theme: str = "blue"
    skill_used: str = "custom"
    generation_method: str = ""
    gen_eval_attempts: int = 1
    gen_eval_time: float = 0.0
    gen_eval_errors: int = 0
    layout: str = ""
    model: str = ""

    model_config = {"extra": "allow"}


class BlueprintSchema(BaseModel):
    """전체 블루프린트 구조 — AI 생성 결과의 최종 형태"""

    main_page: MainPageSpec
    metadata: BlueprintMetadata = Field(default_factory=BlueprintMetadata)
    blocks: list[dict[str, Any]] = Field(default_factory=list)
    databases: list[dict[str, Any]] = Field(default_factory=list)
    sub_pages: list[dict[str, Any]] = Field(default_factory=list)

    model_config = {"extra": "allow"}
