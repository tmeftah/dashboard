from flask import Blueprint

recovers = Blueprint("recovers", __name__)

from . import views
