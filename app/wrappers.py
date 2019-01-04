from functools import wraps
from flask import request, abort, json


def json_required(f):
    from app import errors

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.json:
            v = f(*args, **kwargs)
        else:
            v = abort(400)
        return v
    return decorated_function
