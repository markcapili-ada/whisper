import os

from flask import current_app

from app.tasks.transcription_task import diarized_transcription_task, live_transcription, transcribe_task
from app.utils import get_file_absolute


class TranscriptionActions:
    @staticmethod
    def transcribe_request(filename, is_webhook=False, webhook_url=None):
        file_format = filename.split('.')[-1]
        transcribe_task.apply_async(args=[filename, file_format, is_webhook, webhook_url])
        current_app.logger.info(f"Transcription request for {filename} sent")

    @staticmethod
    def live_transcript_start(data):
        filename = data.get('filename')
        chunk_second = int(data.get('chunk_second'))
        job = live_transcription.apply_async(args=[filename, chunk_second])
        return {"message": f"Live transcription request started", "id": job.id}

    @staticmethod
    def live_transcript_end(data):
        id = data.get("id")
        filename = data.get('filename')
        try:
            current_app.extensions["celery"].control.revoke(id, terminate=True)
        except Exception as e:
            current_app.logger.error(f"Error revoking live transcription: {e}")
            return {"message": "Failed to stop the live transcription."}

        # Cleanup: Remove the audio from recordings
        recordings_dir = get_file_absolute('recordings')
        recordings_dir = recordings_dir / filename
        if os.path.isfile(recordings_dir):
            os.remove(recordings_dir)

        return {"message": f"Live transcption for {id} is cancelled"}

    def transcribe_diarized_request(
        self,
        agent_audio_filename,
        client_audio_filename,
        unique_id,
        webhook_url=None,
        combined_audio_filename=None,
    ):
        diarized_transcription_task.apply_async(
            args=[
                agent_audio_filename,
                client_audio_filename,
                unique_id,
                webhook_url,
                combined_audio_filename,
            ]
        )
        current_app.logger.info(f"Transcribe request for {agent_audio_filename} and {client_audio_filename} sent")
