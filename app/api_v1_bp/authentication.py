from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.verify_password()
def verify_password(email, password):
    '''
     Because this type of user authentication will be used only in the API blueprint,
     the Flask-HTTPAuth extension is initialized in the blueprint package,
     and not in the application package like other extensions.
     The email and password are verified using the existing support in the User model.
     The verification callback returns True when the login is valid or False otherwise.
     Anonymous logins are supported, for which the client must send a blank email field.

    :param email: email address of client
    :param password: password of client
    :return:
    '''