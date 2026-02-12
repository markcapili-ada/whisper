from functools import wraps
from typing import Callable

from flask import request
from pydantic import ValidationError
from werkzeug.exceptions import BadRequest, NotFound


def validate_request():
    def wrapper(func: Callable):
        @wraps(func)
        def decorator(*args, **kwargs):
            body_type: type = func.__annotations__.get("body")

            if body_type:
                json_body = request.get_json()
                if json_body is None:
                    raise BadRequest("Missing body params")
                try:
                    # Use Pydantic's validation
                    body = body_type.model_validate(json_body)
                    kwargs['body'] = body
                except ValidationError as e:
                    # Format Pydantic validation errors
                    errors = []
                    for error in e.errors():
                        errors.append({'field': ' -> '.join(str(x) for x in error['loc']), 'message': error['msg'], 'type': error['type']})
                    raise BadRequest({'message': 'Validation error', 'errors': errors})
                except Exception as e:
                    raise BadRequest(f"Invalid JSON body: {str(e)}")

            return func(*args, **kwargs)

        return decorator

    return wrapper
