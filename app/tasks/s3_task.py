from celery import shared_task
from flask import current_app

from app.utils import get_file_absolute


@shared_task(bind=True, max_retries=3)
def upload_file_to_s3_task(self, file_name, s3_upload_url):
    from app import create_app

    app, _ = create_app()
    with app.app_context():
        from app.services.audio_service import AudioService

        audio_service = AudioService()

        try:

            file_path = get_file_absolute("uploads") / file_name
            audio_service.upload_file_to_S3(file_path, s3_upload_url)

        except Exception as e:
            current_app.logger.error(f"[upload_file_to_s3_task] An error occurred: {e}")
            retry_delay = 5 * (2**self.request.retries)
            self.retry(exc=e, countdown=retry_delay)
