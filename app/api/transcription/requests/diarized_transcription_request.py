from typing import Optional

from app.api.base_request import BaseRequest


class DiarizedTranscriptionRequest(BaseRequest):
    agent_audio_filename: str
    client_audio_filename: str
    unique_id: str
    webhook_url: str
    temporary_upload_url: Optional[str] = None
    combined_audio_filename: Optional[str] = None
