from flask import request, render_template, flash, redirect, url_for
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError

from . import companies as bp
from .. import db_session
from ..models import Companies


@bp.route("/", methods=["GET"])
@login_required
def index():
    companies = db_session.query(Companies).all()
    return render_template("companies/index.html", companies=companies)


@bp.route("/", methods=["POST"])
@login_required
def add_companies():

    name = request.form.get("name")
    email = request.form.get("email")
    company_type = request.form.get("company_type", type=int)
    phone = request.form.get("phone")

    if company_type == 0:
        customer = True
        supplier = False

    if company_type == 1:
        customer = False
        supplier = True

    if company_type == 2:
        customer = True
        supplier = True

    new_company = Companies(
        name=name,
        email=email,
        customer=customer,
        supplier=supplier,
        phone=phone,
    )

    try:
        db_session.add(new_company)
        db_session.commit()

    except SQLAlchemyError as e:
        print(e)
        db_session.rollback()
        flash("db error", category="error")

    else:
        flash("Un nouveau Tier ajouter", category="success")

    return redirect(url_for(".index"))
