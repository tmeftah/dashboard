from flask import Blueprint

costs = Blueprint("costs", __name__)

from . import views
