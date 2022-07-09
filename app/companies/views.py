from flask import request, render_template, flash, redirect, url_for
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError

from . import companies as bp
from .. import db
from ..models import Companies


@bp.route("/", methods=["GET"])
@login_required
def index():
    companies = db.session.query(Companies).all()
    return render_template("companies/index.html", companies=companies)


@bp.route("/", methods=["POST"])
@login_required
def add_companies():

    name = request.form.get("name")
    email = request.form.get("email")
    company_type = request.form.get("company_type", type=int)
    phone = request.form.get("phone")

    company = db.session.query(Companies).filter(Companies.name == name).first()

    if company:
        flash("Le Fournissuer/Client exist deja. Le nom doit être unique!!!", category="warning")
        return redirect(url_for(".index"))

    if company_type == 0:
        customer = True
        supplier = False

    if company_type == 1:
        customer = False
        supplier = True

    # if company_type == 2:
    #     customer = True
    #     supplier = True

    new_company = Companies(
        name=name,
        email=email,
        customer=customer,
        supplier=supplier,
        phone=phone,
    )

    try:
        db.session.add(new_company)
        db.session.commit()

    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="danger")

    else:
        flash("Un nouveau Tier ajouter", category="success")

    return redirect(url_for(".index"))


@bp.route("/<int:id>", methods=["GET"])
@login_required
def get_sale_by_id(id):

    company = db.session.query(Companies).filter(Companies.id == id).first()

    if not company:
        flash("Le Fournissuer/Client n'exist pas !!!")
        return redirect(url_for(".index"))

    return render_template("/companies/_id.html", company=company)


@bp.route("/<int:id>", methods=["POST"])
@login_required
def update_companies(id):

    company = db.session.query(Companies).filter(Companies.id == id).first()

    if not company:
        flash("Le Fournissuer/Client n'exist pas !!!", category="warning")
        return redirect(url_for(".index"))

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

    company.name = name
    company.email = email
    company.customer = customer
    company.supplier = supplier
    company.phone = phone

    try:

        db.session.commit()

    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="danger")

    else:
        flash("Le Fournissuer/Client modiffier", category="success")

    return redirect(url_for(".index"))


@bp.route("/remove/<int:id>", methods=["POST"])
@login_required
def remove_companies(id):

    company = db.session.query(Companies).filter(Companies.id == id).first()

    if not company:
        flash("Le Fournissuer/Client n'exist pas !!!", category="warning")
        return redirect(url_for(".index"))
    db.session.delete(company)
    try:

        db.session.commit()
        flash("Le Fournissuer/Client supprimer !!!", category="success")

    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="danger")

    return redirect(url_for(".index"))
