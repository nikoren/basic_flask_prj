from flask import Flask
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

from celery import Celery
from config import config, Config

mail = Mail()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth_bp.login'

bootstrap = Bootstrap()

manager = Manager()

db = SQLAlchemy()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

def create_app(config_name):
    # create app instance
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # initialize all extensions - extension specific to any BP should be initialized in BP itself(e.g HTTPAuth)
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    # moment.init_app(app)
    mail.init_app(app)
    celery.conf.update(app.config)

    # Attach routes and custom errors here
    from main_bp import main_bp
    app.register_blueprint(main_bp)

    from auth_bp import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from api_v1_bp import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    return app

