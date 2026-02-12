import os

from flask import request, send_file
from flask_restx import Resource
from werkzeug.exceptions import BadRequest, NotFound

from app.helpers.file_helper import is_file_type_supported
from app.services.audio_service import AudioService


class FileResource(Resource):
    def get(self):
        """
        Serve a file based on the provided filename
        """
        audio_service = AudioService()
        filename = request.args.get('filename')
        if not filename or not is_file_type_supported(filename):
            raise BadRequest("File is invalid")

        file_path = audio_service.get_file(filename)
        if file_path is None:
            raise NotFound(description=f"File {filename} not found")

        try:
            return send_file(file_path, as_attachment=True, download_name=filename)
        except Exception as e:
            return {'message': f'Error serving file: {str(e)}'}, 500
