import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    PROJECT_NAME = 'EXAMPLE' # Update the project here
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SUBJECT_PREFIX = '[{}]'.format(PROJECT_NAME)
    MAIL_SENDER = '{} Admin'.format(PROJECT_NAME)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMINS = os.environ.get('{}_ADMINS'.format(PROJECT_NAME)) or ['nikoren@gmail.com',]
    PERMISSIONS = [
        {
            'name': 'admin',
            'description': 'Provides access to following actions: All actions'
        },
        {
            'name': 'read',
            'description': 'Provides basic access to read the information'
        }
    ]
    ROLES = [
        {
            'name': 'Admin',
            'description': 'Role assigned to site administrator and provides full access to all features',
            'permissions': ['admin', 'read'],
            'is_default': False
        },
        {
            'name': 'User',
            'description': 'Default roole assigned to basic user',
            'permissions': ['read'],
            'is_default': True
        }
    ]
    USERS = []

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'nikoren2safari'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'safari11safari@'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
    #                           'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/{}'.format(Config.PROJECT_NAME.lower())

    USERS = [
        {
            'username': 'test_admin',
            'email': 'testadmin@gmail.com',
            'role': 'Admin',
            'confirmed': True,
            'password': 'test11'
        },
        {
            'username': 'test_user',
            'email': 'testuser@gmail.com',
            'role': 'User',
            'confirmed': True,
            'password': 'test11'
        }
    ]


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(basedir, 'data.sqlite')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

