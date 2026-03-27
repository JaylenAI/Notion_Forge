from pydantic import BaseModel


class ChatMessage(BaseModel):
    content: str
    notion_token: str | None = None
    parent_page_id: str | None = None


class ChatResponse(BaseModel):
    type: str  # ai_response | progress | complete | error
    content: str | None = None
    metadata: dict | None = None
