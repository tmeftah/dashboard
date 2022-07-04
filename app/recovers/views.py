import datetime
from flask import request, render_template, flash, redirect, url_for
from flask_login import login_required
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from . import recovers as bp
from .. import db_session
from ..models import Recovers, Companies, PaymentMethod, SalesCategories
from ..utilities.utils import get_sold_clients


@bp.route("/", methods=["GET"])
@login_required
def index():
    recovers = db_session.query(Recovers).order_by(desc(Recovers.date)).all()
    companies = db_session.query(Companies).filter_by(customer=True).all()

    paymentmethod = (
        db_session.query(PaymentMethod).filter(PaymentMethod.name.not_like("Credit")).all()
    )

    return render_template(
        "/recovers/index.html",
        recovers=recovers,
        paymentmethod=paymentmethod,
        companies=companies,
        get_sold_clients=get_sold_clients,
    )


@bp.route("/", methods=["POST"])
@login_required
def add_recovers():
    categorie_id = request.form.get("categorie_id", type=int)
    company_id = request.form.get("company_id", type=int)
    payment_id = request.form.get("payment_id", type=int)
    date = request.form.get("date")
    amount = request.form.get("amount")
    comment = request.form.get("comment")

    document_number = request.form.get("document_number")
    due_date = request.form.get("due_date")

    new_recover = Recovers(
        # categorie_id=categorie_id,
        company_id=company_id,
        paymentmethod_id=payment_id,
        date=datetime.datetime.strptime(date, "%Y-%m-%d"),
        amount=amount,
        comment=comment,
    )

    if payment_id in [2, 3]:
        new_recover.due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d")
        new_recover.document_number = document_number

    try:
        db_session.add(new_recover)
        db_session.commit()
        # upload_file(new_recover) # TODO: uplaod
    except SQLAlchemyError as e:
        print(e)
        db_session.rollback()
        flash("db error", category="error")

    else:
        flash("Recovers ajouter", category="success")

    return redirect(url_for(".index"))


@bp.route("/<int:id>", methods=["GET"])
@login_required
def get_recovers_by_id(id):

    recover = db_session.query(Recovers).filter(Recovers.id == id).first()

    if not recover:
        flash("Recouvrement n'exist pas !!!", category="warning")
        return redirect(url_for(".index"))

    companies = db_session.query(Companies).filter_by(customer=True).all()
    paymentmethod = db_session.query(PaymentMethod).filter(PaymentMethod.id.notin_([4])).all()

    return render_template(
        "/recovers/_id.html",
        recover=recover,
        companies=companies,
        paymentmethod=paymentmethod,
    )


@bp.route("/<int:id>", methods=["POST"])
@login_required
def update_recovers(id):

    recover = db_session.query(Recovers).filter(Recovers.id == id).first()

    if not recover:
        flash("Recouvrement n'exist pas !!!")
        return redirect(url_for(".index"))

    company_id = request.form.get("company_id", type=int)
    payment_id = request.form.get("payment_id", type=int)
    date = request.form.get("date")
    amount = request.form.get("amount")
    comment = request.form.get("comment")

    document_number = request.form.get("document_number")
    due_date = request.form.get("due_date")

    recover.company_id = company_id
    recover.paymentmethod_id = payment_id
    recover.date = datetime.datetime.strptime(date, "%Y-%m-%d")
    recover.amount = amount
    recover.comment = comment

    recover.due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d")
    recover.document_number = document_number or "NOP"

    try:

        db_session.commit()
        # upload_file(recover) # TODO: upload

    except SQLAlchemyError as e:
        print(e)
        db_session.rollback()
        flash("db error", category="error")

    else:
        flash("Recouvrement modiffier", category="success")

    return redirect(url_for(".index"))


@bp.route("/remove/<int:id>", methods=["POST"])
@login_required
def remove_recovers(id):

    recover = db_session.query(Recovers).filter(Recovers.id == id).first()

    if not recover:
        flash("Recouvrement n'exist pas !!!", category="warning")
        return redirect(url_for(".index"))
    db_session.delete(recover)
    try:

        db_session.commit()
        flash("Recouvrement supprimer !!!", category="success")

    except SQLAlchemyError as e:
        print(e)
        db_session.rollback()
        flash("db error", category="danger")

    return redirect(url_for(".index"))
