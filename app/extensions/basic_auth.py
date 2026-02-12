import base64
from functools import wraps

# from app.config.backdoor_config import settings
from flask import request
from werkzeug.exceptions import BadRequest, Unauthorized

from app.config.basic_auth_config import settings


def basic_auth_middleware(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth or 'Basic' not in auth:
            raise Unauthorized('Missing or invalid Authorization header')

        try:
            token = auth.split(' ')[1]
            decoded_token = base64.b64decode(token).decode('utf-8')
            username, password = decoded_token.split(':')

            if username != settings.username or password != settings.password:
                raise Unauthorized('Unauthorized')

        except Exception as e:
            raise BadRequest('Invalid Authorization header format')

        return func(*args, **kwargs)

    return decorated_function
