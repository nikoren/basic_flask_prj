from . import db
import sys
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer
from flask import current_app, url_for
from sqlalchemy.orm.exc import NoResultFound
from .utils import split_url


class ValidationError(ValueError):
    '''
    Throw in case of request validation error
    This can be used when some attributes that are expected in the body of request were not found

    '''
    pass


class AnonymousUser(AnonymousUserMixin):
    '''
    Class that is registered as the class of the object
    that is assigned to current_user when the user is not logged in
    '''

    def can(self, permissions):
        '''
        Method expected by flask-login
        '''
        return False

    def is_admin(self):
        '''
        Method expected by flask-login
        '''
        return False


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True, index=True)
    confirmed = db.Column(db.Boolean(), default=False)
    role = db.relationship('Role', back_populates='users')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

        # Role assignment when user created
        if self.role is None:
            if self.email in current_app.config['ADMINS']:
                self.role = Role.query.filter_by(name='Admin').first()
            if self.role is None:
                self.role = Role.query.filter_by(is_default=True).first()
            current_app.logger.debug('{} assigned to User {} '.format(self.role.name, self.email))

    def export_to_dict(self):
        '''
        Represent current user as dictionary

        Representation of a resource offered to clients does not need to be identical
        to the internal representation of the corresponding database model.

        :return: dict: kye:value of most of user's attributes, some attributes are ommited for privacy
            {usr_attr: usr_attr_value...}
        '''
        export_to_dictd_user = {
            'id': self.id,
            'self_url': self.url,
            'username': self.username,
            'email': self.email,
            'confirmed': self.confirmed,
            'role': self.role.url
        }
        return export_to_dictd_user

    def import_from_dict(self, user_dict):
        '''
        Get user from Dictionary, can be used for extracting user from JSON/XML...

        :param user_dict:  Dictionary
        :return: User(self)
        '''

        #role url
        if 'role' in user_dict:
            endpoint, args = split_url(user_dict['role'])
            if endpoint != 'api_bp.get_role' or 'id' not in args:
                raise ValidationError("Invalid role URL: {}".format(user_dict['role']))

            # role id
            try:
                self.role = Role.query.filter_by(id=(args['id'])).one()
            except NoResultFound as e:
                raise ValidationError('Invalid role id {}: {}'.format(args['id'], e.args[0]))

        try:
            self.username = user_dict['username']
            self.email = user_dict['email']
        except KeyError as e:
            raise ValidationError('Invalid User: missing requiered args {}'.format(e.args[0]))

        # confirmed is optional
        if 'confirmed' in user_dict:
            self.confirmed = user_dict['confirmed'] == 'true'

        return self



    @property
    def url(self):
        return url_for('api_bp.get_user', id=self.id, _external=True)

    @staticmethod
    def insert_cfg_users():

        # Make sure roles are populated
        Role.insert_cfg_roles()

        for cfg_user in current_app.config['USERS']:

            try:
                db_role = Role.query.filter_by(name=cfg_user['role']).one()
            except NoResultFound as e:
                current_app.logger.exception(
                    'Could not add User {}, no such role in DB {}'.format(
                        cfg_user['name'], cfg_user['role']))
                raise

            # Role is in DB - otherwise can't get here
            try:
                db_user = User.query.filter_by(username=cfg_user['username']).one()
            except NoResultFound:
                current_app.logger.debug(
                    'User {} is not in DB - creating it with {} and role {}'.format(
                        cfg_user['username'], cfg_user, db_role))
                db_user = User(
                    username=cfg_user['username'],
                    email=cfg_user['email'],
                    role=db_role,
                    confirmed=cfg_user['confirmed']
                )

            # User in DB - update it per need
            for cfg_att_name in cfg_user.keys():
                if not (cfg_att_name.startswith('_') or
                        cfg_att_name == 'role'):
                    if getattr(db_user,cfg_att_name) != getattr(cfg_user, cfg_att_name):
                        current_app.logger.debug('Updating user {}, setting {} to {}'.format(
                        db_user.id, cfg_att_name, cfg_user[cfg_att_name])
                        )
                        setattr(db_user, cfg_att_name, cfg_user[cfg_att_name])

            db_user.role = db_role
            db_user.password = cfg_user['password']
            db.session.merge(db_user)

        db.session.commit()

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
            current_app.current_app.logger.debug('Token loaded: {}'.format(token))
        except Exception:
            current_app.current_app.logger.exception("Couldn't load the token")
            return False

        if token.get('id') == self.id:
            current_app.current_app.logger.debug('Token id match users id')
            self.confirmed = True
            db.session.add(self)
            current_app.current_app.logger.debug('User {} confirmed'.format(self))
            return True
        current_app.current_app.logger.warning("Token {} doesnt't match 'id:{}'".format(token, self.id))
        return False

    def can(self, permissions):
        '''
        Check if all the permissions are allowed for current user
        :param permissions: List of permissions
        :return: Boolean status
        '''

        for permission in permissions:
            if isinstance(permission, str):
                try:
                    permission = Permission.query.filter_by(name=permission).one()
                except NoResultFound as e:
                    current_app.current_app.logger.debug('No such permission {}, exiting'.format(permission))
                    return False
            if permission.name not in \
                    [p.name for p in self.role.permissions]:
                return False
        return True

    def is_admin(self):
        if self.role.name == 'Admin':
            return True

    def generate_auth_token(self, expiration):
        """
        Encodes user id into token token

        :param expiration: time in seconds for token to expire
        :return: token
        """
        s = TimedJSONWebSignatureSerializer(
            current_app.config['SECRET_KEY'], expires_in=expiration)

        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        """
        Extracts user id from encoded token,

        this methos is static, as there is no way to find our which user runs it until he authenticates himself

        :param token: authentication token
        :return: User id or None
        """
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            current_app.logger.debug('Could not load token, token verification failed - returning None')
            return None

        current_app.logger.debug('Loaded token data is {}'.format(data))
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.username


@login_manager.user_loader
def user_loader(user_id):
    """
    Flask-Login requires the application to set up a callback function
    that loads a user, given the identifier.

    """
    return User.query.get(int(user_id))


# Association table for use<->role many-to-many relationship
permissions_in_role = db.Table(
    'permissions_in_role',
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)


class Permission(db.Model):
    '''
    Provides access to a single action
    '''
    __tablename__ = 'permissions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, nullable=False, unique=True)
    description = db.Column(db.String(length=1024), nullable=True)

    # many-to-many Role<->Permission
    roles = db.relationship(
        'Role',
        secondary='permissions_in_role',
        back_populates='permissions',
    )

    def export_to_dict(self):
        return {
            'id': self.id,
            'self_url': self.url,
            'name': self.name,
            'description': self.description,
            'roles': [role.url for role in self.roles]
        }

    @property
    def url(self):
        return url_for('api_bp.get_permission', id=self.id, _external=True)

    @staticmethod
    def insert_cfg_permissions():
        cfg_permissions = current_app.config['PERMISSIONS']
        # Add missing permissions
        for cfg_permission in cfg_permissions:
            try:
                db_permission = Permission.query.filter_by(
                    name=cfg_permission['name']).one()
            except NoResultFound:
                db_permission = Permission(
                    name=cfg_permission['name'],
                    description=cfg_permission.get('description')
                )
            if db_permission.name != cfg_permission['name']:
                db_permission.name = cfg_permission['name']
            if (cfg_permission.get('description') is not None
                and cfg_permission.get('description') != db_permission.description):
                db_permission.description = cfg_permission['description']

            current_app.current_app.logger.debug('Adding {} permission'.format(db_permission.name))
            db.session.merge(db_permission)

        current_app.current_app.logger.debug('finished adding all permissions')
        db.session.commit()

    def __repr__(self):
        return 'Permission <{}>'.format(self.name)


class Role(db.Model):
    '''
    Represent set of permissions that can be assigned to user
    '''
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False, index=True)
    description = db.Column(db.String(1024), nullable=True)
    # based on this attribute default role can be set to new users
    is_default = db.Column(db.Boolean, default=False, index=True)
    # many-to-many Roles<->Permissions
    permissions = db.relationship(
        'Permission',
        secondary='permissions_in_role',
        back_populates='roles')

    # one-to-many Role -> Users
    users = db.relationship(
        'User',
        back_populates='role',
        lazy='dynamic')


    def export_to_dict(self):
        '''
        Helper method that represent user as dictionary,
        this can be used later for converting to XML/JSON...

        :return: dict{role_attr:value,...}

        '''
        return {
            'id': self.id,
            'self_url': self.url,
            'name': self.name,
            'description': self.description,
            'is_default': self.is_default,
            'permissions': [p.url for p in self.permissions],
            'users': [u.url for u in self.users]}

    @property
    def url(self):
        return url_for('api_bp.get_role', id=self.id, _external=True)

    @staticmethod
    def insert_cfg_roles():
        Permission.insert_cfg_permissions()
        for cfg_role in current_app.config['ROLES']:
            current_app.current_app.logger.debug('adding role {}'.format(cfg_role['name']))
            try:
                db_role = Role.query.filter_by(name=cfg_role.get('name')).one()
            except NoResultFound:
                db_role = Role(
                    name=cfg_role.get('name'),
                    description=cfg_role.get('description')
                )

            for cfg_attr in cfg_role.keys():
                current_app.current_app.logger.debug('cfg_attr is {}'.format(cfg_attr))
                if not cfg_attr.startswith('_'):
                    if getattr(db_role, cfg_attr) != cfg_role.get(cfg_attr):
                        if cfg_attr == 'permissions':
                            try:

                                for cfg_permission in cfg_role['permissions']:
                                    db_role.permissions.extend(Permission.query.filter_by(name=cfg_permission).all())
                            except NoResultFound as e:
                                current_app.current_app.logger.exception('Failed on permission {} '.format(cfg_permission))
                                raise
                        else:
                            setattr(db_role, cfg_attr, cfg_role.get(cfg_attr))

            db.session.merge(db_role)

        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name
