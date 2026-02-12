from sys import stderr

from flask import jsonify
from flask_pydantic import validate
from flask_restx import Resource

from app.api.base_request import BaseRequest
from app.api.test.actions.test_actions import TestActions
from app.api.validate_request import validate_request
from app.extensions.basic_auth import basic_auth_middleware


class Requestsss(BaseRequest):
    message: str = None


class TestResource(Resource):
    @validate_request()
    @basic_auth_middleware
    def post(self, body: Requestsss):
        print(f'Received: {body.model_dump()}', file=stderr)
        test = TestActions()
        message = test.hello('test')
        return jsonify(message)

    @validate_request()
    def get(self):

        test = TestActions()
        message = test.hello('test')

        return jsonify(message)
