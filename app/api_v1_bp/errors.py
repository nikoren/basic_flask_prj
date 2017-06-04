from ..api_errors import RestApiErrors
from . import api_bp
from flask import current_app

# You can costumize you errors here by subclassing RestApiErrors class or creating your own

@api_bp.errorhandler(401)
def auth_error(e):
    """
    Overrides HTML errors and raises REST friendly errors instead

    :param e: werkzeug.exceptions.Unauthorized
    """
    return RestApiErrors.unauthorized_401(e.description)

@api_bp.errorhandler(403)
def forbidden_error(e):
    """
    Overrides HTML errors and raises REST friendly errors instead

    :param e: werkzeug.exceptions.Forbidden
    :return:
    """
    return RestApiErrors.forbidden_403(e.description)

@api_bp.errorhandler(404)
def not_found(e):
    '''
    Overrides HTML errors and raises REST friendly errors instead
    :param e: werkzeug.exceptions.NotFound
    :return:
    '''
    return RestApiErrors.not_found_404(e.description)

@api_bp.errorhandler(405)
def not_allowed(e):
    """
    Overrides HTML errors and raises REST friendly errors instead

    :param e: werkzeug.exceptions.MethodNotAllowed
    """
    return RestApiErrors.not_allowed_405(e.description)

@api_bp.errorhandler(500)
def internal_server_error(e):
    """
    Overrides HTML errors and raises REST friendly errors instead

    :param e:  werkzeug.exceptions.InternalServerError
    :return:
    """
    return RestApiErrors.internal_server_error_500(e.description)
