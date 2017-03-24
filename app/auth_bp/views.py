from flask import render_template
from . import auth_bp

@auth_bp.route('/login')
def login():
    render_template('auth_bp/login')