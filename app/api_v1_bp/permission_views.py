from flask import jsonify
from authentication_views import auth
from . import api_bp
from ..decorators import permissions_required
from .. import models
from sqlalchemy.orm.exc import NoResultFound


from errors import RestApiErrors

@permissions_required(['admin'])
@api_bp.route('/permission/<int:id>')
def get_permission(id):
    try:
        role = models.Role.query.filter_by(id=id).one()
    except NoResultFound:
        return RestApiErrors.not_found_404('No permission {} found'.format(id))
    return jsonify(role.export_to_dict())