from flask import Blueprint, request, jsonify, g
from app.db import get_db
from .validation import validate_user_data
from app.services.user import get_user_data
from app.middleware.auth import token_required


bp_routers = Blueprint('admin', __name__)


@bp_routers.route("/users", methods=['GET'])
@token_required
def get_users():
    """
        For getting all users
    """
    # This route only for admin
    if g.auth_data['level_id'] != 3:
        return jsonify({
            'status': 'Fail',
            'message': 'UnAuthorized user'
        }), 401

    cursor = get_db().cursor()
    query = "SELECT * FROM user"
    results = cursor.execute(query).fetchall()
    results = [dict(row) for row in results]

    return jsonify({
        'data': results,
        'status': 'OK',
        'message': 'Successfully retrieve users data'
    }), 200


@bp_routers.route("/user", methods=['POST'])
@token_required
def create_user():
    """
        For creating users
    """
    # This route only for admin
    if g.auth_data['level_id'] != 3:
        return jsonify({
            'status': 'Fail',
            'message': 'UnAuthorized user'
        }), 401

    data = request.get_json()
    db = get_db()
    cursor = db.cursor()
    validation_results = validate_user_data(data)
    if validation_results:
        return jsonify({
            'data': data,
            'status': 'Fail',
            'message': validation_results
        }), 404

    # By default user's status is set to False
    data.setdefault('status', False)

    try:
        query = "INSERT INTO user (username, password, level_id, email, fullName, status) " \
                "VALUES (?, ?, ?, ?, ?, ?)"
        cursor.execute(query, (data["username"], data["password"], data["level_id"],
                               data["email"], data["full_name"], data["status"]))
        db.commit()

    except db.IntegrityError:
        return jsonify({
            'data': data,
            'status': 'Fail',
            'message': f"User Exists {data['username']} with email {data['email']}"
        }), 404

    return jsonify({
            'data': data,
            'status': 'OK',
            'message': 'Successfully created new user'
        }), 200


@bp_routers.route("/user/<user_id>", methods=['PUT'])
@token_required
def update_user(user_id):
    """
        For updating existing users
        Uses overriding for every request
    """
    # This route only for admin
    if g.auth_data['level_id'] != 3:
        return jsonify({
            'status': 'Fail',
            'message': 'UnAuthorized user'
        }), 401

    data = request.get_json()
    data['user_id'] = user_id
    db = get_db()
    cursor = db.cursor()
    user_data = get_user_data(db, user_id)
    if user_data is None:
        return jsonify({
            'data': data,
            'status': 'Fail',
            'message': f"User with userId {user_id} not exists"
        }), 404

    # Overriding un-filled fields
    data.setdefault('username', user_data['username'])
    # TODO: Add hash encryption for password
    data.setdefault('password', user_data['password'])
    data.setdefault('level_id', user_data['level_id'])
    data.setdefault('email', user_data['email'])
    data.setdefault('fullName', user_data['fullName'])
    data.setdefault('status', user_data['status'])

    # To cater sqlite conversion of boolean: True - 1, False - 0
    if data['status'] == 0:
        status = False
    else:
        status = True
    data['status'] = status

    validation_results = validate_user_data(data)
    if validation_results:
        return jsonify({
            'data': data,
            'status': 'Fail',
            'message': validation_results
        }), 404

    try:
        query = "INSERT INTO user (username, password, level_id, email, fullName, status) " \
                "VALUES (?, ?, ?, ?, ?, ?)"
        cursor.execute(query, (data["username"], data["password"], data["level_id"],
                               data["email"], data["full_name"], data["status"]))
        db.commit()

    except db.IntegrityError:
        return jsonify({
            'data': data,
            'status': 'Fail',
            'message': f"User Exists {data['username']} with email {data['email']}"
        }), 404

    return jsonify({
            'data': data,
            'status': 'OK',
            'message': 'Successfully updated user'
        }), 200


@bp_routers.route("/user/<user_id>", methods=['DELETE'])
@token_required
def delete_user(user_id):
    """
        For deleting existing user
    """
    # This route only for admin
    if g.auth_data['level_id'] != 3:
        return jsonify({
            'status': 'Fail',
            'message': 'UnAuthorized user'
        }), 401

    db = get_db()
    cursor = db.cursor()
    user_data = get_user_data(db, user_id)
    if user_data is None:
        return jsonify({
            'data': {'id': user_id},
            'status': 'Fail',
            'message': f"User with userId {user_id} not exists"
        }), 404

    delete_query = "DELETE FROM user WHERE id=?"
    cursor.execute(delete_query, user_id)
    db.commit()

    return jsonify({
        'data': {'id': user_id},
        'status': 'OK',
        'message': f"User with userId {user_id} successfully deleted"
    })


def component_blueprint():
    """
    This returns the component blueprint

    """
    return bp_routers
