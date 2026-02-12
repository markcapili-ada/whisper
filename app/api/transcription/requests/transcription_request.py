from app.api.base_request import BaseRequest


class TranscriptionRequest(BaseRequest):
    filename: str
    webhook_url: str
