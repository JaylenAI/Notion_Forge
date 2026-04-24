from pydantic import BaseModel, Field


class TemplateGenerateRequest(BaseModel):
    prompt: str = Field(min_length=2, max_length=2000)
    notion_token: str = Field(min_length=1, max_length=200)
    parent_page_id: str = Field(min_length=1, max_length=50, pattern=r"^[a-f0-9-]+$")
    options: dict | None = None


class TemplateGenerateResponse(BaseModel):
    success: bool
    notion_url: str | None = None
    page_id: str | None = None
    summary: dict | None = None


class TemplatePreviewRequest(BaseModel):
    prompt: str = Field(min_length=2, max_length=2000)


class TemplatePreviewResponse(BaseModel):
    blueprint: dict


class DetectProviderRequest(BaseModel):
    api_key: str = Field(default="", max_length=500)


class DetectProviderResponse(BaseModel):
    provider: str
    models: list[dict] = []
    error: str | None = None
