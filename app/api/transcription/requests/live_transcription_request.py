from typing import Optional

from app.api.base_request import BaseRequest


class LiveTranscriptionRequest(BaseRequest):
    filename: str
    chunk_second: Optional[int] = None
    id: Optional[str] = None
