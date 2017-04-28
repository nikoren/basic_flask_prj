from . import db
import sys
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer
from flask import current_app
from sqlalchemy.orm.exc import NoResultFound


class AnonymousUser(AnonymousUserMixin):
    '''
    Class that is registered as the class of the object
    that is assigned to current_user when the user is not logged in
    '''

    def can(self, permissions):
        return False

    def is_admin(self):
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
                self.role = Role.query.filter_by(default=True).first()

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
                    current_app.logger.debug('No such permission {}, exiting'.format(permission))
                    return False
            if permission.name not in \
                    [p.name for p in self.role.permissions]:
                return False
        return True

    def is_admin(self):
        if self.role.name == 'Admin':
            return True

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

    @staticmethod
    def insert_permissions():
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
                and cfg_permission.get('description') != db_permission.description ):
                db_permission.description = cfg_permission['description']

            current_app.logger.debug('Adding {} permission'.format(db_permission.name))
            db.session.merge(db_permission)

        current_app.logger.debug('finished adding all permissions')
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

    @staticmethod
    def insert_roles():
        Permission.insert_permissions()
        for cfg_role in current_app.config['ROLES']:
            current_app.logger.debug('adding role {}'.format(cfg_role['name']))
            try:
                db_role = Role.query.filter_by(name=cfg_role.get('name')).one()
            except NoResultFound:
                db_role = Role(
                    name=cfg_role.get('name'),
                    description = cfg_role.get('description')
                )

            for cfg_attr in cfg_role.keys():
                current_app.logger.debug('cfg_attr is {}'.format(cfg_attr))
                if not cfg_attr.startswith('_'):
                    if getattr(db_role, cfg_attr) != cfg_role.get(cfg_attr):
                        if cfg_attr == 'permissions':
                            try:

                                for cfg_permission in cfg_role['permissions']:
                                    db_role.permissions.extend(Permission.query.filter_by(name=cfg_permission).all())
                            except NoResultFound as e:
                                current_app.logger.exception('Failed on permission {} '.format(cfg_permission))
                                sys.exit()
                        else:
                            setattr(db_role, cfg_attr, cfg_role.get(cfg_attr))

            db.session.merge(db_role)

        db.session.commit()



    def __repr__(self):
        return '<Role %r>' % self.name

