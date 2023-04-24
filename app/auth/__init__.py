import datetime
from flask import Blueprint, request, jsonify
from app.db import get_db
import jwt
import os


bp_routers = Blueprint('auth', __name__)


@bp_routers.route("/auth", methods=['POST'])
def authenticate():
    data = request.get_json()
    cursor = get_db().cursor()
    query = "SELECT * FROM user " \
            "WHERE username = ? " \
            "AND password = ?"
    res = cursor.execute(query, (data["username"], data["password"])).fetchone()
    if res is None:
        return 'Invalid Username and Password', 401
    secrets = os.environ.get('JWT_SECRET')

    encoded_jwt = jwt.encode({
            'id': res["id"],
            'level_id': res["level_id"],
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
        },
        secrets, algorithm='HS256')

    return jsonify({
        'token': encoded_jwt,
    }), 200


def component_blueprint():
    """
    This returns the component blueprint

    """
    return bp_routers
