from . import main_bp

from flask import render_template, request, jsonify

# if the errorhandler decorator is used, the handler will only be invoked for errors
# that originate in the blueprint.
# To install application-wide error handlers, the app_errorhandler must be used instead.
@main_bp.app_errorhandler(404)
def page_not_found(e):

    # for rest apis construct and return JSON , otherwise flask use HTML by default, checks the Accept request header
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response

    return render_template('404.html'), 404


@main_bp.app_errorhandler(500)
def internal_server_error(e):

    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'Internal server error'})
        response.status_code = 500
        return response

    return render_template('500.html'), 500

