from flask import jsonify, make_response, request
from flask_restx import Resource
from werkzeug.exceptions import BadRequest, NotFound

from app.api.transcription.actions.transcription_actions import TranscriptionActions
from app.api.transcription.requests.diarized_transcription_request import DiarizedTranscriptionRequest
from app.api.validate_request import validate_request
from app.extensions.basic_auth import basic_auth_middleware
from app.extensions.webhook import webhook_middleware
from app.helpers.file_helper import is_file_type_supported
from app.services.audio_service import AudioService
from app.tasks.s3_task import upload_file_to_s3_task


class TranscribeDiarizedRequestResource(Resource):

    @validate_request()
    @webhook_middleware
    def post(self, body: DiarizedTranscriptionRequest):
        audio_service = AudioService()
        agent_audio_filename = body.agent_audio_filename
        client_audio_filename = body.client_audio_filename
        combined_audio_filename = body.combined_audio_filename
        filenames = [agent_audio_filename, client_audio_filename]
        unique_id = body.unique_id
        webhook_url = body.webhook_url

        if body.temporary_upload_url:
            combined_audio_file_path, _ = audio_service.get_file(combined_audio_filename)
            print(f"[Transcribe diarized request combined_audio_file_path] {combined_audio_file_path}")

            upload_file_to_s3_task.delay(
                combined_audio_filename,
                body.temporary_upload_url,
            )

        print(f"[Transcribe diarized request received] {agent_audio_filename} and {body.temporary_upload_url} with unique id {unique_id}")

        if not agent_audio_filename or not client_audio_filename or not all(is_file_type_supported(filename) for filename in filenames):
            raise BadRequest("Files are invalid")

        file_paths = []
        for filename in filenames:
            file_path, file_size = audio_service.get_file(filename)
            if file_path is not None:
                file_paths.append(file_path)
            else:
                raise NotFound(description=f"File {filename} not found")

        TranscriptionActions().transcribe_diarized_request(
            body.agent_audio_filename,
            body.client_audio_filename,
            body.unique_id,
            webhook_url=webhook_url,
            combined_audio_filename=combined_audio_filename,
        )

        response = make_response(jsonify({"message": f"Transcribe request sent "}))
        response.status_code = 202
        print(f"[Transcribe diarized request received] {agent_audio_filename} and {client_audio_filename} with unique id {unique_id}")
        return response
