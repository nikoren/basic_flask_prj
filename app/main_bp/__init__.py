from flask import Blueprint
main_bp = Blueprint('main_bp', __name__)

#  Importing views and errors handlers causes them to be associated with the blueprint
#  they are imported at the bottom of the app/__init__.py script to avoid circular
#  dependencies, because views.py and errors.py need to import the main_bp .
from . import views, errors
