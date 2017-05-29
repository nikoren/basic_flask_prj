from . import main_bp
from . import forms
from .. import models
from .. import db
from flask import session, redirect, flash, url_for, render_template, jsonify
from flask_login import login_required
from ..decorators import admin_required, permissions_required
from sqlalchemy.orm.exc import NoResultFound

@main_bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@main_bp.route('/admins', methods=['GET'])
@admin_required
@login_required
def admins():
    return 'For admins only'


@main_bp.route('/read_only_required', methods=['GET'])
@login_required
@permissions_required(['read',])
def read_only_required():
    return 'For users with read_only permissions'

@main_bp.route('/clear_session/<value>')
def clear_session(value='all'):
    if value != 'all':
        if value in session.keys():
            session[value] = None
            flash('{} was removed from session'.format(value))
    else:
        session.clear()
        flash('Session was cleared', category='danger')
    return redirect(url_for('.index'))

