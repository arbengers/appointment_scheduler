from functools import wraps
from flask import request, jsonify, g
import jwt
import os


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'UnAuthorized Requests, Missing Token'}), 401

        try:
            # decoding the payload to fetch the stored details
            secrets = os.environ.get('JWT_SECRET')
            data = jwt.decode(token, secrets, algorithms='HS256')
            g.auth_data = data
        except Exception as err:
            print(err)
            return jsonify({
                'message': 'UnAuthorized Requests, Invalid Token'
            }), 401

        return f(*args, **kwargs)

    return decorated
