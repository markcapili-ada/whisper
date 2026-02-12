import os
from sys import stderr

from flask import current_app, jsonify, request
from flask_pydantic import validate
from flask_restx import Resource
from werkzeug.exceptions import BadRequest, NotFound

from app.api.base_request import BaseRequest
from app.config.enums import AudioMeta
from app.extensions.basic_auth import basic_auth_middleware
from app.tasks.transcription_task import transcribe_task
from app.utils import get_file_absolute


class TranscribeResource(Resource):
    @validate()
    @basic_auth_middleware
    def post(self):
        SUPPORTED_FORMATS = AudioMeta.SUPPORTED_FORMATS.value
        MAX_FILE_SIZE = 20
        # Check if a file is part of the request
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        retranscribe = request.args.get('retranscribe')
        json_params = request.form.get('params')

        # Save the current position of the file pointer for restoration later
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        max_file_size = MAX_FILE_SIZE * 1024 * 1024
        if file_size > max_file_size:
            return jsonify({"error": "File size exceeds the limit"}), 400

        # Check for file formats
        file_format = file.filename.split('.')[-1]
        if file_format not in SUPPORTED_FORMATS:
            return jsonify({"error": f"Unsupported file format: {file_format}. Supported formats are: {', '.join(SUPPORTED_FORMATS)}"}), 400
        filename_without_ext = file.filename.replace(f".{file_format}", "")

        transcriptions_dir = get_file_absolute("transcriptions")
        filename_json = f"{filename_without_ext}.json"

        transcripts_loc = transcriptions_dir / filename_json

        if os.path.isfile(transcripts_loc):
            if retranscribe != None and int(retranscribe) == 1:
                current_app.logger.info(f"Retranscribing {file.filename}")
            else:
                return jsonify({"message": "Conflict: Already transcribed"}), 409

        try:
            uploads_dir = get_file_absolute("uploads")
            file_path = uploads_dir / file.filename
            file.save(file_path)
        except Exception as e:
            print(f"Error saving file: {e}")
            return jsonify({"error": "Failed to save file"}), 500

        if not os.path.isfile(file_path):
            return jsonify({"error": "File not found after saving"}), 500

        transcribe_task.queue(file.filename, file_format)
        return jsonify({"message": f"Transcribe request sent"}), 202
