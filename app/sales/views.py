import datetime
from flask import request, render_template, flash, redirect, url_for
from flask_login import login_required
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from . import sales as bp
from .. import db
from ..models import Sales, Companies, SalesCategories, PaymentMethod


@bp.route("/", methods=["GET"])
@login_required
def index():
    categorie = request.args.get("categorie", type=int, default=0)

    paymentme = request.args.get("paymentmethod", type=int, default=0)

    query = db.session.query(Sales)

    if categorie:
        query = query.filter(Sales.categorie_id == categorie)

    if paymentme:
        query = query.filter(Sales.paymentmethod_id == paymentme)

    sales = query.order_by(desc(Sales.date)).all()

    companies = db.session.query(Companies).filter_by(customer=True).all()
    salescategories = db.session.query(SalesCategories).all()
    paymentmethod = db.session.query(PaymentMethod).filter(PaymentMethod.id.notin_([7])).all()

    return render_template(
        "/sales/index.html",
        sales=sales,
        companies=companies,
        salescategories=salescategories,
        paymentmethod=paymentmethod,
    )


@bp.route("/", methods=["POST"])
@login_required
def add_sales():

    company_id = request.form.get("company_id", type=int)
    payment_id = request.form.get("payment_id", type=int)
    date = request.form.get("date")
    amount = request.form.get("amount")
    comment = request.form.get("comment")

    document_number = request.form.get("document_number")
    due_date = request.form.get("due_date")

    new_sale = Sales(
        company_id=company_id,
        paymentmethod_id=payment_id,
        date=datetime.datetime.strptime(date, "%Y-%m-%d"),
        amount=amount,
        comment=comment,
    )
    if payment_id in [2, 3]:
        new_sale.due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d")
        new_sale.document_number = document_number

    try:
        db.session.add(new_sale)
        db.session.commit()
        # upload_file(new_sale) #TODO: uplaod file

    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="error")

    else:
        flash("Chiffre d'affaire ajouter", category="success")

    return redirect(url_for(".index"))


@bp.route("/<int:id>", methods=["GET"])
@login_required
def get_sale_by_id(id):

    sale = db.session.query(Sales).filter(Sales.id == id).first()

    if not sale:
        flash("Chiffre d'affaire n'exist pas !!!")
        return redirect(url_for(".index"))

    companies = db.session.query(Companies).filter_by(customer=True).all()
    salescategories = db.session.query(SalesCategories).all()
    paymentmethod = db.session.query(PaymentMethod).filter(PaymentMethod.id.notin_([7])).all()

    return render_template(
        "/sales/_id.html",
        sale=sale,
        companies=companies,
        salescategories=salescategories,
        paymentmethod=paymentmethod,
    )


@bp.route("/<int:id>", methods=["POST"])
@login_required
def update_sales(id):

    sale = db.session.query(Sales).filter(Sales.id == id).first()

    if not sale:
        flash("Chiffre d'affaire n'exist pas !!!", category="warning")
        return redirect(url_for(".index"))

    company_id = request.form.get("company_id", type=int)
    payment_id = request.form.get("payment_id", type=int)
    date = request.form.get("date")
    amount = request.form.get("amount")
    comment = request.form.get("comment")

    document_number = request.form.get("document_number")
    due_date = request.form.get("due_date")

    sale.company_id = company_id
    sale.paymentmethod_id = payment_id
    sale.date = datetime.datetime.strptime(date, "%Y-%m-%d")
    sale.amount = amount
    sale.comment = comment

    sale.due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d")
    sale.document_number = document_number or "NOP"

    try:

        db.session.commit()
        # upload_file(sale) #TODO: uplaod file

    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="danger")

    else:
        flash("Chiffre d'affaire modiffier", category="success")

    return redirect(url_for(".index"))


@bp.route("/remove/<int:id>", methods=["POST"])
@login_required
def remove_sales(id):

    sale = db.session.query(Sales).filter(Sales.id == id).first()

    if not sale:
        flash("Chiffre d'affaire n'exist pas !!!", category="warning")
        return redirect(url_for("sales.index"))
    db.session.delete(sale)
    try:

        db.session.commit()
        flash("Chiffre d'affaire supprimer !!!", category="success")

    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="danger")

    return redirect(url_for(".index"))


@bp.route("/salescategories")
@login_required
def salescategories():
    return render_template("sales/categories.html")
