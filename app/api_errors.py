from flask import jsonify



class RestApiErrors(object):
    """
    This class implements all the helper functions for API errors
    """

    @staticmethod
    def forbidden_403(message):
        """
        403 Forbidden - The authentication credentials sent with the request are insufficient for the request.

        :param message:  Message to return to client
        """
        response = jsonify({'error': 'forbidden', 'message': message})
        response.status_code = 403
        return response

    @staticmethod
    def unauthorized_401(message):
        """
        401 Unauthorized - The request does not include authentication information.

        :param message:  Message to return to client
        """
        response = jsonify({'error': 'unauthorized', 'message': message})
        response.status_code = 401
        return response

    @staticmethod
    def not_found_404(message):
        """
        404 Not found - The resource referenced in the URL was not found.

        :param message:  Message to return to client
        """
        response = jsonify({'error': 'not found', 'message': message})
        response.status_code = 404

    @staticmethod
    def not_allowed_405(message):
        """
        405 Method not allowed - The request method requested is not supported for the given resource.

        :param message:  Message to return to client
        """
        response = jsonify({'error': 'not allowed', 'message': message})
        response.status_code = 405

    @staticmethod
    def internal_server_error_500(message):
        """
        500 Internal server error - An unexpected error has occurred while processing the request.

        :param message:  Message to return to client
        """
        response = jsonify({'error': 'internal server error', 'message': message})
        response.status_code = 500

