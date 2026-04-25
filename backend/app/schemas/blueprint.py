import logging
from typing import Any

from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger("notionforge.schemas")


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


# ── AI 원시 콘텐츠 검증 ────────────────────────────────────


class AIContentSpec(BaseModel):
    """AI가 생성하는 원시 콘텐츠 구조 — Structured Output 검증"""

    title: str = ""
    icon: str = ""
    color: str = "blue"
    skill: str = ""
    blocks: list[dict[str, Any]] = Field(default_factory=list)
    databases: list[dict[str, Any]] = Field(default_factory=list)
    sub_pages: list[dict[str, Any]] = Field(default_factory=list)
    faq: list[Any] = Field(default_factory=list)

    model_config = {"extra": "allow"}


def validate_ai_content(raw: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """AI 출력을 Pydantic으로 검증 + 교정. (교정된 dict, 에러 목록) 반환.

    - 검증 통과 → 정규화된 dict + 빈 에러 목록
    - 검증 실패 → 원본 dict + 에러 메시지 목록 (Gen-Eval 재시도 트리거용)
    """
    errors: list[str] = []

    # db_properties → databases 정규화 (단일 DB 래핑)
    if "db_properties" in raw and "databases" not in raw:
        raw = {
            **raw,
            "databases": [
                {
                    "title": raw.get("title", "DB"),
                    "db_properties": raw["db_properties"],
                    "views": raw.get("views", ["table"]),
                    "sample_items": raw.get("sample_items", []),
                }
            ],
        }

    try:
        validated = AIContentSpec.model_validate(raw)
        result = validated.model_dump(exclude_none=True)

        if not result.get("blocks"):
            errors.append("Pydantic: blocks 배열이 비어있습니다.")
        if not result.get("databases"):
            errors.append("Pydantic: databases 배열이 비어있습니다.")

        for di, db in enumerate(result.get("databases", [])):
            props = db.get("db_properties", db.get("properties", {}))
            has_title = any(v == "title" or (isinstance(v, dict) and v.get("type") == "title") for v in props.values())
            if not has_title:
                errors.append(f"Pydantic: databases[{di}]에 title 타입 속성이 없습니다.")

        if errors:
            return raw, errors
        return result, []

    except ValidationError as e:
        for err in e.errors():
            loc = ".".join(str(x) for x in err["loc"])
            errors.append(f"Pydantic: {loc} — {err['msg']}")
        return raw, errors


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
