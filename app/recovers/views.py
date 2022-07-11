import datetime
from flask import request, render_template, flash, redirect, url_for
from flask_login import login_required
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from . import recovers as bp
from .. import db
from ..models import Recovers, Companies, PaymentMethod, SalesCategories
from ..utilities.utils import get_sold_clients
from ..utilities.utils2 import toDate, compare


@bp.route("/", methods=["GET"])
@login_required
def index():

    s_company = request.args.get("s_company", type=int, default=0)
    s_paymentmethod = request.args.get("s_paymentmethod", type=int, default=0)
    s_op = request.args.get("s_op", type=str, default="")
    s_amount = request.args.get("s_amount", type=float, default=0.0)
    s_start_date = request.args.get("s_start_date", type=toDate, default="")
    s_end_date = request.args.get("s_end_date", type=toDate, default="")

    query = Recovers.query()

    if s_company > 0:
        query = query.filter(Recovers.company_id == s_company)

    if s_paymentmethod > 0:
        query = query.filter(Recovers.paymentmethod_id == s_paymentmethod)

    if s_op in ["big", "small", "equal"]:
        if s_amount >= 0:
            query = query.filter(compare(Recovers.amount, s_amount, s_op))

    if s_start_date:
        query = query.filter(Recovers.date >= s_start_date)
    if s_end_date:
        query = query.filter(Recovers.date <= s_end_date)

    recovers = query.order_by(desc(Recovers.date)).all()

    companies = Companies.query().filter_by(customer=True).all()

    paymentmethod = db.session.query(PaymentMethod).filter(PaymentMethod.id.notin_([7])).all()

    return render_template(
        "/recovers/index.html",
        recovers=recovers,
        paymentmethod=paymentmethod,
        companies=companies,
        s_company=s_company,
        s_paymentmethod=s_paymentmethod,
        s_op=s_op,
        s_amount=s_amount,
        s_start_date=s_start_date,
        s_end_date=s_end_date,
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
        db.session.add(new_recover)
        db.session.commit()
        # upload_file(new_recover) # TODO: uplaod
    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="error")

    else:
        flash("Recovers ajouter", category="success")

    return redirect(url_for(".index"))


@bp.route("/<int:id>", methods=["GET"])
@login_required
def get_recovers_by_id(id):

    recover = Recovers.query().filter(Recovers.id == id).first()

    if not recover:
        flash("Recouvrement n'exist pas !!!", category="warning")
        return redirect(url_for(".index"))

    companies = Companies.query().filter_by(customer=True).all()
    paymentmethod = db.session.query(PaymentMethod).filter(PaymentMethod.id.notin_([4])).all()

    return render_template(
        "/recovers/_id.html",
        recover=recover,
        companies=companies,
        paymentmethod=paymentmethod,
    )


@bp.route("/<int:id>", methods=["POST"])
@login_required
def update_recovers(id):

    recover = Recovers.query().filter(Recovers.id == id).first()

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

        db.session.commit()
        # upload_file(recover) # TODO: upload

    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="error")

    else:
        flash("Recouvrement modiffier", category="success")

    return redirect(url_for(".index"))


@bp.route("/remove/<int:id>", methods=["POST"])
@login_required
def remove_recovers(id):

    recover = Recovers.query().filter(Recovers.id == id).first()

    if not recover:
        flash("Recouvrement n'exist pas !!!", category="warning")
        return redirect(url_for(".index"))
    db.session.delete(recover)
    try:

        db.session.commit()
        flash("Recouvrement supprimer !!!", category="success")

    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="danger")

    return redirect(url_for(".index"))
