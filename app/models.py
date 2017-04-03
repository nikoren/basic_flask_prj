from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer
from flask import current_app

class Role(UserMixin, db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')
    email = db.Column(db.String(64), unique=True, index=True)

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True, index=True)
    confirmed = db.Column(db.Boolean(), default=False)

    @property
    def password(self):

        '''
        Write only property of User , password can be only changed , you can't read it

        Raises AttributeError
        '''

        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def password_is_correct(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        token = s.dumps({'id': self.id})
        return token

    def confirm_valid_token(self, token):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        try:
            token = s.loads(token)
            current_app.logger.debug('Token loaded: {}'.format(token))
        except Exception:
            current_app.logger.exception("Couldn't load the token")
            return False

        if token.get('id') == self.id:
            current_app.logger.debug('Token id match users id')
            self.confirmed = True
            db.session.add(self)
            current_app.logger.debug('User {} confirmed'.format(self))
            return True
        current_app.logger.warning("Token {} doesnt't match 'id:{}'".format(token, self.id))
        return False

    def __repr__(self):
        return '<User %r>' % self.username


@login_manager.user_loader
def user_loader(user_id):
    """
    Flask-Login requires the application to set up a callback function
    that loads a user, given the identifier.

    """
    return User.query.get(int(user_id))

