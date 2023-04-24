from flask import Blueprint, jsonify


bp_routers = Blueprint('health_check', __name__)


@bp_routers.route("/", methods=['GET'])
def health_check():
    return jsonify({
        'status': 'OK',
    }), 200


def component_blueprint():
    """
    This returns the component blueprint

    """
    return bp_routers
