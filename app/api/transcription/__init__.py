from flask_restx import Namespace

from app.api.transcription.resources.transcribe_diarized_request_resource import TranscribeDiarizedRequestResource
from app.api.transcription.resources.transcribe_live_resource import TranscribeLiveResource
from app.api.transcription.resources.transcribe_request_resource import TranscribeRequestResource
from app.api.transcription.resources.transcribe_resource import TranscribeResource


transcription_namespace = Namespace('transcribe', path='/transcribe')
transcription_namespace.add_resource(
    TranscribeResource,
    '/',
)
transcription_namespace.add_resource(TranscribeRequestResource, '/request')
transcription_namespace.add_resource(
    TranscribeLiveResource,
    '/live/<string:action>',
)
transcription_namespace.add_resource(
    TranscribeDiarizedRequestResource,
    '/diarize',
)
