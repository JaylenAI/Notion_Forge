from app.config import settings
from app.notion.client import NotionClient


def get_notion_client() -> NotionClient:
    return NotionClient(token=settings.notion_api_key)
