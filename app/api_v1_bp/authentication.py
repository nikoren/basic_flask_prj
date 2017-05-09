from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from ..models import AnonymousUser, User, Role
from sqlalchemy.orm.exc import NoResultFound
from errors import RestApiErrors
from . import api_v1_bp
from ..decorators import permissions_required

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email, password):
    '''
     Push current_user to g global object for view functions (required by HTTPAuth extension) and verifies validity of password

     Like Flask-Login, Flask-HTTPAuth makes no assumptions about the procedure required to verify user credentials,
     so this information is given in this callback function.

     Because this type of user authentication will be used only in the API blueprint,
     the Flask-HTTPAuth extension is initialized in the blueprint package,
     and not in the application package like other extensions.

     The email and password are verified using the existing support in the User model.
     The verification callback returns True when the login is valid or False otherwise.
     Anonymous logins are supported, for which the client must send a blank email field.

     Because user credentials are being exchanged with every request, it is extremely important that the API routes
     are exposed over secure HTTP (https) so that all requests and responses are encrypted.

    :param email: email address of client
    :param password: password of client

    :return: verification_status: boolean status of password verification (True/False)
    '''

    if email == '':
        g.current_user = AnonymousUser()
        return False

    try:
        user = User.query.filter_by(email=email).one()
    except NoResultFound as e:
        g.current_user = AnonymousUser()
        return False

    g.current_user = user
    return user.password_is_correct(password)


@auth.error_handler
def auth_error():
    """
    When the authentication credentials are invalid, the server returns a 401 error to the client.
    Flask-HTTPAuth generates a response with this status code by default,
    but to ensure that the response is consistent with other errors returned by the API,
    the error response is customized
    :return:
    """
    return RestApiErrors.unauthorized_401('invalid credentials')


@api_v1_bp.before_request
@auth.login_required
def before_request():
    """
    since all the routes in the blueprint need to be protected in the same way,
    the login_required decorator can be included once in a before_request handler for the blueprint
    :return:
    """
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return RestApiErrors.forbidden_403('Unconfirmed account')

# To protect single route, the auth.login_required decorator can be used but not required - as all routes protected
@permissions_required(['admin'])
@api_v1_bp.route('/roles')
def get_roles():
    """
    Sample route function - list available roles
    :return:
    """
    roles = Role.query.all()
    return jsonify({'roles': [role.name for role in roles]})
