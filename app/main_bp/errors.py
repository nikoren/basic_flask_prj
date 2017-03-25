from . import main_bp

from flask import render_template

# if the errorhandler decorator is used, the handler will only be invoked for errors
# that originate in the blueprint.
# To install application-wide error handlers, the app_errorhandler must be used instead.
@main_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@main_bp.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500