from flask import render_template, request, flash, redirect, url_for
from werkzeug.security import check_password_hash
from flask_login import login_user, login_required, logout_user
from . import auth as bp
from .. import db
from ..models import User


@bp.route("/")
def index():
    return "ok"


@bp.route("/login", methods=["GET"])
def login():
    return render_template("login.html")


@bp.route("/login", methods=["POST"])
def login_post():

    email = request.form.get("email")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False

    user = db.session.query(User).filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash("Please check your login details and try again.")
        return redirect(
            url_for("auth.login")
        )  # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for("dash.dashboard"))


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for(".login"))
