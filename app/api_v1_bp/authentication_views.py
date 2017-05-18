from flask import g, jsonify, current_app
from flask_httpauth import HTTPBasicAuth
from ..models import AnonymousUser, User, Role
from sqlalchemy.orm.exc import NoResultFound
from errors import RestApiErrors
from . import api_bp
from ..decorators import permissions_required

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password):
    '''
     Push current_user to "g" (global object) for view functions (required by HTTPAuth extension)
     and verifies validity of password/token by returning boolean status

     Like Flask-Login, Flask-HTTPAuth makes no assumptions about the procedure required to verify user credentials,
     so this information is given in this callback function, extension only expects to have current user in `g`
     credentials are sent with each request according to REST requirements  whenever Flask-HTTPAuth
     needs to protect route , also, it is up to this function to notify http_auth extension whether authentication was successful

     in case of email/password combination, both of arguments are required,
     in case of token authentication , password should be empty string

     boolean "token_used" attributes added to user to specify authentication method
     if one of the authentication methods was successful


     Because this type of user authentication will be used only in the API blueprint,
     the Flask-HTTPAuth extension is initialized in the blueprint package,
     and not in the application package like other extensions.

     The email and password are verified using the existing support in the User model.
     The verification callback returns True when the login is valid or False otherwise.
     Anonymous logins are supported, for which the client must send a blank email field.

     Because user credentials are being exchanged with every request, it is important that the API routes
     are exposed over https so that all requests and responses are encrypted.

    :param email_or_token: email or temp auth token of client
    :param password: password of client

    :return: verification_status: boolean status of password verification (True = verified, False = not verified)
    '''

    # No authentication method selected
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return False

    # Token authentication
    if password == '':
        g.token_used = True
        g.current_user = User.verify_auth_token(email_or_token)
        return g.current_user is not None

    # Email/password authentication
    try:
        user = User.query.filter_by(email=email_or_token).one()
    except NoResultFound:
        g.current_user = AnonymousUser()
        return False
    g.current_user = user
    g.token_used = True
    return user.password_is_correct(password)


@auth.error_handler
def auth_error():
    """
    When the authentication credentials are invalid, Flask-HTTPAuth generates a response
    with the 401 error to the client.

    to ensure that the response is consistent with other errors returned by the API,
    the error response is customized
    :return:
    """
    return RestApiErrors.unauthorized_401('invalid credentials')


@api_bp.before_request
@auth.login_required
def before_request():
    """
    since all the routes in the blueprint need to be protected in the same way,
    the login_required decorator can be included once in a before_request handler for the blueprint
    :return:
    """
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return RestApiErrors.forbidden_403('Unconfirmed account')


@api_bp.route('/get_token')
def get_token():
    '''
    Generate token for users authenticated with Username/password,

    :return:
    '''

    # reject users that are trying to get token with no credentials or existing old token
    if g.current_user.is_anonymous() \
            or g.token_used:
        return RestApiErrors.unauthorized_401('Invalid credentials')

    # generate tokens
    return jsonify(
        {
            'token': g.current_user.generate_auth_token(
                expiration=current_app.config['API_TOKEN_EXPIRATION_SECONDS']),
            'expiration': current_app.config['API_TOKEN_EXPIRATION_SECONDS']
        }
    )


# To protect single route, the auth.login_required decorator can be used
# but not required - as all routes protected on blueprint level
@auth.login_required
@permissions_required(['admin'])
@api_v1_bp.route('/roles')
def get_roles():
    """
    Sample route function - list available roles
    :return:
    """
    roles = Role.query.all()
    return jsonify({'roles': [role.name for role in roles]})
