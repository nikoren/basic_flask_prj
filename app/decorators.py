from functools import wraps
from flask import abort
from flask_login import current_user


def permissions_required(permissions):
    """
    Decorator that check permissions, can be used to protect certain
    routes from unauthorized uses
    :param permissions List
    :return: error code 403, the Forbidden HTTP error, when the current user does not have the requested permissions.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permissions):
                abort(403)
            return f(*args,**kwargs)
        return decorated_function

    return decorator

def admin_required(f):
    return permissions_required(['admin'])(f)
