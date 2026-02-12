from flask_jwt_extended.exceptions import JWTExtendedException
from jwt.exceptions import InvalidTokenError

from app.api.file import file_namespace
from app.api.test import test_namespace
from app.api.transcription import transcription_namespace
from app.extensions.api import api


api.add_namespace(transcription_namespace)
api.add_namespace(file_namespace)
api.add_namespace(test_namespace)


@api.errorhandler(JWTExtendedException)
def handle_JWTExtendedException(e: JWTExtendedException):
    raise e


@api.errorhandler(InvalidTokenError)
def handle_InvalidTokenError(e: InvalidTokenError):
    raise e
