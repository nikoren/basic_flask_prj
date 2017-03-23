from flask import Flask
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import config
# from flask_moment import Moment
# from flask_mail import Mail


bootstrap = Bootstrap()
manager = Manager()
db = SQLAlchemy()
# moment = Moment()
# mail = Mail()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    config[config_name].init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    # moment.init_app(app)
    # mail.init_app(app)

    # Attach routes and custom errors here
    from main import main_blueprint
    app.register_blueprint(main_blueprint)

    return app

