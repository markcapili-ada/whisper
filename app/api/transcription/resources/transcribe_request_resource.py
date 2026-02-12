from flask import jsonify, make_response, request
from flask_restx import Resource
from werkzeug.exceptions import BadRequest, NotFound

from app.api.transcription.actions.transcription_actions import TranscriptionActions
from app.api.transcription.requests.transcription_request import TranscriptionRequest
from app.api.validate_request import validate_request
from app.extensions.basic_auth import basic_auth_middleware
from app.extensions.webhook import webhook_middleware
from app.helpers.file_helper import is_file_type_supported
from app.services.audio_service import AudioService
from app.tasks.s3_task import upload_file_to_s3_task


class TranscribeRequestResource(Resource):
    @validate_request()
    @basic_auth_middleware
    def get(self):
        audio_service = AudioService()
        filename = request.args.get('filename')
        s3_upload_url = request.args.get('temporary_upload_url')

        if not filename or not is_file_type_supported(filename):
            raise BadRequest("File is invalid")

        file_path, file_size = audio_service.get_file(filename)
        if file_path is None:
            raise NotFound(description=f"File {filename} not found")

        upload_file_to_s3_task.delay(filename, s3_upload_url)
        TranscriptionActions.transcribe_request(filename)

        response = make_response(jsonify({"message": f"Transcribe request sent"}))
        response.status_code = 202
        return response

    @validate_request()
    @webhook_middleware
    def post(self, body: TranscriptionRequest):
        audio_service = AudioService()
        filename = body.filename
        webhook_url = body.webhook_url

        if not filename or not is_file_type_supported(filename):
            raise BadRequest("File is invalid")

        file_path, file_size = audio_service.get_file(filename)
        if file_path is None:
            raise NotFound(description=f"File {filename} not found")

        TranscriptionActions.transcribe_request(filename, is_webhook=True, webhook_url=webhook_url)

        response = make_response(jsonify({"message": f"Transcribe request sent"}))
        response.status_code = 202
        return response
