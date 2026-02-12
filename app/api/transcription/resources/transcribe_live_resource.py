from flask import jsonify, make_response
from flask_restx import Resource
from werkzeug.exceptions import BadRequest, NotFound

from app.api.transcription.actions.transcription_actions import TranscriptionActions
from app.api.transcription.requests.live_transcription_request import LiveTranscriptionRequest
from app.api.validate_request import validate_request
from app.extensions.basic_auth import basic_auth_middleware
from app.helpers.file_helper import is_file_type_supported
from app.services.audio_service import AudioService


class TranscribeLiveResource(Resource):
    @validate_request()
    @basic_auth_middleware
    def post(
        self,
        action,
        body: LiveTranscriptionRequest,
    ):
        body = body.model_dump()
        filename = body['filename']
        if not is_file_type_supported(filename):
            raise BadRequest("File is invalid")
        if action == "start":
            message = TranscriptionActions.live_transcript_start(body)
            response = make_response(jsonify(message))
            response.status_code = 202
            return response
        elif action == "end":
            if body["id"] != None:
                audio_service = AudioService()

                file_path, file_size = audio_service.get_file(filename)
                if file_path is None:
                    raise NotFound(description=f"File {filename} not found")

                message = TranscriptionActions.live_transcript_end(body)
                response = make_response(jsonify(message))
                response.status_code = 202
                return response
            else:
                raise BadRequest(description="id is required")

        else:
            raise NotFound(description="Action not found")
