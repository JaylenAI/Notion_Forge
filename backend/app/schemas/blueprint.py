from pydantic import BaseModel


class IntentResult(BaseModel):
    intent: str  # CREATE | MODIFY | QUESTION | CONFIRM | REJECT
    template_type: str  # dashboard | tracker | bookmark | ...
    title: str | None = None
    color_theme: str = "default"
    databases: list[dict] | None = None
    sub_pages: list[str] | None = None
    missing_info: list[str] | None = None
    confidence: float = 0.0
    modify_type: str | None = None  # add_property, add_view, add_db, add_relation, add_formula, add_subpage, add_block, delete_property, change_property, change_view
