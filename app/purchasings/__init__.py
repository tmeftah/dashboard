from flask import Blueprint

purchasings = Blueprint("purchasings", __name__)

from . import views
