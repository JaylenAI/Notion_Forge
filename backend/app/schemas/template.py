from pydantic import BaseModel


class TemplateGenerateRequest(BaseModel):
    prompt: str
    notion_token: str
    parent_page_id: str
    options: dict | None = None


class TemplateGenerateResponse(BaseModel):
    success: bool
    notion_url: str | None = None
    page_id: str | None = None
    summary: dict | None = None


class TemplatePreviewRequest(BaseModel):
    prompt: str


class TemplatePreviewResponse(BaseModel):
    blueprint: dict
