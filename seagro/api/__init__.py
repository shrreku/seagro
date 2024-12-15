from flask import Blueprint

bp = Blueprint('api', __name__)

from seagro.api import jobs, users
