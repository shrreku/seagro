from flask import jsonify, request
from flask_login import login_required, current_user
from seagro.api import bp
from seagro.models.user import User
from seagro import db

@bp.route('/users/profile', methods=['GET'])
@login_required
def get_profile():
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'first_name': current_user.first_name,
        'last_name': current_user.last_name
    })
