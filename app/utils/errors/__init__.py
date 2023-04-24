import logging
from flask import jsonify
from .general_error import GeneralError
from .invalid_body_error import InvalidBodyError


def register_errors(app):
    @app.errorhandler(500)
    def internal_server(ex):
        logging.exception('The server encountered an internal error')
        response = jsonify(status="error", severity='error', message="The server encountered an internal error and was "
                                                                     "unable to complete your request. "
                                                                     "Either the server is overloaded or there is an "
                                                                     "error in the application.")
        response.status_code = 500
        return response

    @app.errorhandler(404)
    def page_not_found(ex):
        logging.exception('An error occurred during a request. page not found')
        response = jsonify(status="error", severity='error', message="page not found")
        response.status_code = 404
        return response

    @app.errorhandler(405)
    def page_not_found(ex):
        logging.exception('An error occurred during a request. page not found')
        response = jsonify(status="error", severity='error', message="Method Not Allowed")
        response.status_code = 405
        return response

    @app.errorhandler(GeneralError)
    @app.errorhandler(InvalidBodyError)
    @app.errorhandler(TimeoutError)
    def handle_all_error(ex):
        # Log the error and stacktrace.
        logging.exception('An error occurred during a request.')
        response = jsonify(status="error", severity=ex.severity, message=ex.error)
        response.status_code = ex.status_code
        return response
