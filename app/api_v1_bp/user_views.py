from flask import jsonify, request, abort
from authentication_views import auth
from . import api_bp
from ..decorators import permissions_required
from .. import models
from sqlalchemy.orm.exc import NoResultFound
from .. import db


# To protect single route, the auth.login_required decorator can be used
# but not required - as all routes protected on blueprint level
# @auth.login_required
# @permissions_required(['admin'])
# @api_bp.route('/roles')
# def get_roles():
#     """
#     Sample route function - list available roles
#     :return:
#     """
#     roles = Role.query.all()
#     return jsonify({'roles': [role.name for role in roles]})

from errors import RestApiErrors


@permissions_required(['admin'])
@api_bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    try:
        user = models.User.query.filter_by(id=id).one()
    except NoResultFound as e:
        abort(404)
    return jsonify(user.export_to_dict())


@permissions_required(['admin'])
@api_bp.route('/users/', methods=['GET'])
def get_users():
    '''
    Returns list of urls for all users. This route intentionally returns URL's and not Data in order
    to use caching which is most efficient when we have only one way to return data - resource by id

    :return:
    '''
    return jsonify({'customers': [u.url for u in
                                  models.User.query.all()]})


@permissions_required(['admin', ])
@api_bp.route('/users/', methods=['POST'])
def new_user():
    user = models.User()
    user.import_from_dict(request.json)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.export_to_dict()), 201, {'Location': user.url}


@permissions_required(['admin', ])
@api_bp.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = models.User.query.get_or_404(id)
    user.import_from_dict(request.json)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.export_to_dict()), 200, {'Location': user.url}

@permissions_required(['admin'])
@api_bp.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = models.User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({}), 204
