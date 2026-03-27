from fastapi import HTTPException


class NotionAuthError(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Notion API 토큰이 유효하지 않습니다")


class NotionPageNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Notion 페이지를 찾을 수 없거나 권한이 없습니다")


class NotionRateLimitError(HTTPException):
    def __init__(self):
        super().__init__(status_code=429, detail="Notion API 요청 한도를 초과했습니다")


class ClaudeApiError(HTTPException):
    def __init__(self, detail: str = "Claude API 호출 중 오류가 발생했습니다"):
        super().__init__(status_code=500, detail=detail)


class BlueprintValidationError(HTTPException):
    def __init__(self, detail: str = "템플릿 구조 검증에 실패했습니다"):
        super().__init__(status_code=422, detail=detail)


class TemplateGenerationError(HTTPException):
    def __init__(self, detail: str = "템플릿 생성 중 오류가 발생했습니다"):
        super().__init__(status_code=500, detail=detail)
