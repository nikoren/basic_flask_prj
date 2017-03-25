from flask import Flask
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth_bp.login'

bootstrap = Bootstrap()

manager = Manager()

db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    config[config_name].init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    # moment.init_app(app)
    # mail.init_app(app)

    # Attach routes and custom errors here
    from main_bp import main_bp
    app.register_blueprint(main_bp)

    from auth_bp import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app

