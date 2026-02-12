from flask_restx import Namespace

from app.api.file.resources.file_resource import FileResource


file_namespace = Namespace('file', path='/file')
file_namespace.add_resource(
    FileResource,
    '/',
)
