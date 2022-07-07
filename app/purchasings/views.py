import datetime
from flask import request, render_template, flash, redirect, url_for
from flask_login import login_required
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from . import purchasings as bp
from .. import db
from ..models import Purchasing, Companies, PaymentMethod, SalesCategories
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

    query = db.session.query(Purchasing)

    if s_company > 0:
        query = query.filter(Purchasing.company_id == s_company)

    if s_paymentmethod > 0:
        query = query.filter(Purchasing.paymentmethod_id == s_paymentmethod)

    if s_op in ["big", "small", "equal"]:
        if s_amount >= 0:
            query = query.filter(compare(Purchasing.amount, s_amount, s_op))

    if s_start_date:
        query = query.filter(Purchasing.date >= s_start_date)
    if s_end_date:
        query = query.filter(Purchasing.date <= s_end_date)

    purchasings = query.order_by(desc(Purchasing.date)).all()

    companies = db.session.query(Companies).filter_by(supplier=True).all()
    salescategories = db.session.query(SalesCategories).all()
    paymentmethod = db.session.query(PaymentMethod).filter(PaymentMethod.id.notin_([7])).all()

    return render_template(
        "/purchasings/index.html",
        purchasings=purchasings,
        companies=companies,
        salescategories=salescategories,
        paymentmethod=paymentmethod,
        s_company=s_company,
        s_paymentmethod=s_paymentmethod,
        s_op=s_op,
        s_amount=s_amount,
        s_start_date=s_start_date,
        s_end_date=s_end_date,
    )


@bp.route("/", methods=["POST"])
@login_required
def add_purchasings():

    payment_id = request.form.get("payment_id", type=int)
    company_id = request.form.get("company_id", type=int)
    date = request.form.get("date")
    amount = request.form.get("amount")
    comment = request.form.get("comment")

    document_number = request.form.get("document_number")
    due_date = request.form.get("due_date")

    new_purchasing = Purchasing(
        paymentmethod_id=payment_id,
        company_id=company_id,
        date=datetime.datetime.strptime(date, "%Y-%m-%d"),
        amount=amount,
        comment=comment,
    )

    if payment_id in [2, 3]:
        new_purchasing.due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d")
        new_purchasing.document_number = document_number

    try:
        db.session.add(new_purchasing)
        db.session.commit()
        # upload_file(new_purchasing) # TODO: upload
    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="error")

    else:
        flash("Achat ajouter", category="success")

    return redirect(url_for(".index"))


@bp.route("/<int:id>", methods=["GET"])
@login_required
def get_purchasings_by_id(id):

    purchasing = db.session.query(Purchasing).filter(Purchasing.id == id).first()

    if not purchasing:
        flash("Achat n'exist pas !!!", category="warning")
        return redirect(url_for(".index"))

    companies = db.session.query(Companies).filter_by(supplier=True).all()
    salescategories = db.session.query(SalesCategories).all()
    paymentmethod = db.session.query(PaymentMethod).filter(PaymentMethod.id.notin_([7])).all()

    return render_template(
        "/purchasings/_id.html",
        purchasing=purchasing,
        companies=companies,
        salescategories=salescategories,
        paymentmethod=paymentmethod,
    )


@bp.route("/<int:id>", methods=["POST"])
@login_required
def update_purchasings(id):

    purchasing = db.session.query(Purchasing).filter(Purchasing.id == id).first()

    if not purchasing:
        flash("Achat n'exist pas !!!")
        return redirect(url_for(".index"))

    company_id = request.form.get("company_id", type=int)
    payment_id = request.form.get("payment_id", type=int)
    date = request.form.get("date")
    amount = request.form.get("amount")
    comment = request.form.get("comment")

    document_number = request.form.get("document_number")
    due_date = request.form.get("due_date")

    purchasing.company_id = company_id
    purchasing.paymentmethod_id = payment_id
    purchasing.date = datetime.datetime.strptime(date, "%Y-%m-%d")
    purchasing.amount = amount
    purchasing.comment = comment

    purchasing.due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d")
    purchasing.document_number = document_number or "NOP"

    try:

        db.session.commit()
        # upload_file(purchasing)# TODO: upload

    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="error")

    else:
        flash("Achat modiffier", category="success")

    return redirect(url_for(".index"))


@bp.route("/remove/<int:id>", methods=["POST"])
@login_required
def remove_purchasings(id):

    purchasing = db.session.query(Purchasing).filter(Purchasing.id == id).first()

    if not purchasing:
        flash("Achat n'exist pas !!!", category="warning")
        return redirect(url_for(".index"))
    db.session.delete(purchasing)
    try:

        db.session.commit()
        flash("Achat supprimer !!!", category="success")

    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="danger")

    return redirect(url_for(".index"))
