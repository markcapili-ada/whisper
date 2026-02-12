import base64
from functools import wraps

# from app.config.backdoor_config import settings
from flask import request
from werkzeug.exceptions import BadRequest, Unauthorized

from app.config.webhook_config import settings as webhook_settings


def webhook_middleware(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('X-Webhook-Token')
        if not token:
            raise Unauthorized('Missing or invalid Authorization header')
        try:
            if token != webhook_settings.secret_key:
                raise Unauthorized('Unauthorized')

        except Exception as e:
            raise BadRequest('Invalid Authorization header format')

        return func(*args, **kwargs)

    return decorated_function
