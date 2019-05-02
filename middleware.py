import os

from flask import request
from functools import wraps
from werkzeug.exceptions import Unauthorized

TOKEN = os.environ.get('TOKEN')


def check_authentication(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.args.get('token')

        if not token or TOKEN != token:
            raise Unauthorized()

        return f(*args, **kwargs)
    return decorated_function
