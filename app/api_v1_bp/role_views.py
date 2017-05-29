from flask import jsonify
from authentication_views import auth
from . import api_bp
from ..decorators import permissions_required
from .. import models
from sqlalchemy.orm.exc import NoResultFound


from errors import RestApiErrors

@permissions_required(['admin'])
@api_bp.route('/role/<int:id>')
def get_role(id):
    try:
        role = models.Role.query.filter_by(id=id).one()
    except NoResultFound:
        return RestApiErrors.not_found_404('No role {} found'.format(id))
    return jsonify(role.export_to_dict())

