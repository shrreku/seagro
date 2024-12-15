from flask import Blueprint

bp = Blueprint('auth', __name__)

from seagro.auth import routes
