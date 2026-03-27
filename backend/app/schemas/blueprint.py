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
