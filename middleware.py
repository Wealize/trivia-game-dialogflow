import os

from flask import request
from functools import wraps
from werkzeug.exceptions import Unauthorized

def is_token_valid(token):
    TOKEN = os.environ.get('TOKEN')
    return token and TOKEN == token


def check_authentication(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_token_valid(request.args.get('token')):
            raise Unauthorized()

        return f(*args, **kwargs)
    return decorated_function
