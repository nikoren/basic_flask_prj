from flask import Blueprint

api_bp = Blueprint('api_bp', __name__)
# Associate view/models... with blueprint
from . import authentication_views, user_views, role_views, permission_views, decorators