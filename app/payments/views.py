import datetime
from flask import request, render_template, flash, redirect, url_for
from flask_login import login_required
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from . import payments as bp
from .. import db
from ..models import Payments, Companies, PaymentMethod, CostsDef
from ..utilities.utils2 import toDate, compare


@bp.route("/", methods=["GET"])
@login_required
def index_purchasings():

    s_company = request.args.get("s_company", type=int, default=0)
    s_paymentmethod = request.args.get("s_paymentmethod", type=int, default=0)
    s_op = request.args.get("s_op", type=str, default="")
    s_amount = request.args.get("s_amount", type=float, default=0.0)
    s_start_date = request.args.get("s_start_date", type=toDate, default="")
    s_end_date = request.args.get("s_end_date", type=toDate, default="")

    query = db.session.query(Payments).filter(Payments.company_id.isnot(None))

    if s_company > 0:
        query = query.filter(Payments.company_id == s_company)

    if s_paymentmethod > 0:
        query = query.filter(Payments.paymentmethod_id == s_paymentmethod)

    if s_op in ["big", "small", "equal"]:
        if s_amount >= 0:
            query = query.filter(compare(Payments.amount, s_amount, s_op))

    if s_start_date:
        query = query.filter(Payments.date >= s_start_date)
    if s_end_date:
        query = query.filter(Payments.date <= s_end_date)

    payments = query.order_by(desc(Payments.date)).all()

    suppliers = db.session.query(Companies).filter_by(supplier=True).all()

    paymentmethod = db.session.query(PaymentMethod).filter(PaymentMethod.id.notin_([7])).all()

    return render_template(
        "/payments/index.html",
        payments=payments,
        paymentmethod=paymentmethod,
        suppliers=suppliers,
        s_company=s_company,
        s_paymentmethod=s_paymentmethod,
        s_op=s_op,
        s_amount=s_amount,
        s_start_date=s_start_date,
        s_end_date=s_end_date,
    )


@bp.route("/costs", methods=["GET"])
@login_required
def index_costs():

    s_company = request.args.get("s_company", type=int, default=0)
    s_paymentmethod = request.args.get("s_paymentmethod", type=int, default=0)
    s_op = request.args.get("s_op", type=str, default="")
    s_amount = request.args.get("s_amount", type=float, default=0.0)
    s_start_date = request.args.get("s_start_date", type=toDate, default="")
    s_end_date = request.args.get("s_end_date", type=toDate, default="")

    query = db.session.query(Payments).filter(Payments.cost_id.isnot(None))

    if s_company > 0:
        query = query.filter(Payments.cost_id == s_company)

    if s_paymentmethod > 0:
        query = query.filter(Payments.paymentmethod_id == s_paymentmethod)

    if s_op in ["big", "small", "equal"]:
        if s_amount >= 0:
            query = query.filter(compare(Payments.amount, s_amount, s_op))

    if s_start_date:
        query = query.filter(Payments.date >= s_start_date)
    if s_end_date:
        query = query.filter(Payments.date <= s_end_date)

    payments = query.order_by(desc(Payments.date)).all()
    paymentmethod = db.session.query(PaymentMethod).filter(PaymentMethod.id.notin_([7])).all()
    cost_defs = db.session.query(CostsDef).all()

    return render_template(
        "/payments/costs.html",
        payments=payments,
        paymentmethod=paymentmethod,
        cost_defs=cost_defs,
        s_company=s_company,
        s_paymentmethod=s_paymentmethod,
        s_op=s_op,
        s_amount=s_amount,
        s_start_date=s_start_date,
        s_end_date=s_end_date,
    )


@bp.route("/", methods=["POST"])
@login_required
def add_payments():
    # categorie_id = request.form.get("categorie_id", type=int)
    payment_id = request.form.get("payment_id", type=int)
    date = request.form.get("date")
    amount = request.form.get("amount")
    comment = request.form.get("comment")

    company_id = request.form.get("company_id", type=int)
    cost_id = request.form.get("cost_id", type=int)

    document_number = request.form.get("document_number")
    due_date = request.form.get("due_date")

    new_payment = Payments(
        # categorie_id=categorie_id,
        company_id=company_id,
        cost_id=cost_id,
        paymentmethod_id=payment_id,
        date=datetime.datetime.strptime(date, "%Y-%m-%d"),
        amount=amount,
        comment=comment,
    )

    if payment_id in [2, 3]:
        new_payment.due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d")
        new_payment.document_number = document_number

    try:
        db.session.add(new_payment)
        db.session.commit()
        # upload_file(new_payment) # TODO: upload
    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="error")

    else:
        flash("Payment ajouter", category="success")

    if company_id:
        return redirect(url_for(".index_purchasings"))

    if cost_id:
        return redirect(url_for(".index_costs"))


@bp.route("/purchasings/<int:id>", methods=["GET"])
@login_required
def get_payment_purchasing_by_id(id):

    payment = db.session.query(Payments).filter(Payments.id == id).first()

    if not payment:
        flash("Le paiement n'exist pas !!!")
        return redirect(url_for(".index_purchasings"))

    suppliers = db.session.query(Companies).filter(Companies.supplier == True).all()
    paymentmethod = db.session.query(PaymentMethod).filter(PaymentMethod.id.notin_([7])).all()

    return render_template(
        "/payments/_id_purchasing.html",
        payment=payment,
        suppliers=suppliers,
        paymentmethod=paymentmethod,
    )


@bp.route("/purchasings/<int:id>", methods=["POST"])
@login_required
def update_payment_purchasing(id):

    payment = db.session.query(Payments).filter(Payments.id == id).first()

    if not payment:
        flash("Le paiement n'exist pas !!!", category="warning")
        return redirect(url_for(".index_purchasings"))

    company_id = request.form.get("company_id", type=int)
    payment_id = request.form.get("payment_id", type=int)
    date = request.form.get("date")
    amount = request.form.get("amount")
    comment = request.form.get("comment")

    document_number = request.form.get("document_number")
    due_date = request.form.get("due_date")

    payment.company_id = company_id
    payment.paymentmethod_id = payment_id
    payment.date = datetime.datetime.strptime(date, "%Y-%m-%d")
    payment.amount = amount
    payment.comment = comment

    payment.due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d")
    payment.document_number = document_number or "NOP"

    try:

        db.session.commit()
        # upload_file(sale) #TODO: uplaod file

    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="danger")

    else:
        flash("Chiffre d'affaire modiffier", category="success")

    return redirect(url_for(".index_purchasings"))


@bp.route("/purchasings/remove/<int:id>", methods=["POST"])
@login_required
def remove_payment_purchasings(id):

    payment = db.session.query(Payments).filter(Payments.id == id).first()

    if not payment:
        flash("Le paiement n'exist pas !!!", category="warning")
        return redirect(url_for(".index_purchasings"))
    db.session.delete(payment)
    try:

        db.session.commit()
        flash("Paiement supprimer !!!", category="success")

    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="danger")

    return redirect(url_for(".index_purchasings"))


# --------------------------- Cost ------------------------------
@bp.route("/costs/<int:id>", methods=["GET"])
@login_required
def get_payment_costs_by_id(id):

    payment = db.session.query(Payments).filter(Payments.id == id).first()

    if not payment:
        flash("Le paiement n'exist pas !!!")
        return redirect(url_for(".index_purchasings"))

    cost_defs = db.session.query(CostsDef).all()
    paymentmethod = db.session.query(PaymentMethod).filter(PaymentMethod.id.notin_([7])).all()

    return render_template(
        "/payments/_id_cost.html",
        payment=payment,
        cost_defs=cost_defs,
        paymentmethod=paymentmethod,
    )


@bp.route("/costs/<int:id>", methods=["POST"])
@login_required
def update_payment_cost(id):

    payment = db.session.query(Payments).filter(Payments.id == id).first()

    if not payment:
        flash("Le paiement n'exist pas !!!", category="warning")
        return redirect(url_for(".index_costs"))

    cost_id = request.form.get("cost_id", type=int)
    payment_id = request.form.get("payment_id", type=int)
    date = request.form.get("date")
    amount = request.form.get("amount")
    comment = request.form.get("comment")

    document_number = request.form.get("document_number")
    due_date = request.form.get("due_date")

    payment.cost_id = cost_id
    payment.paymentmethod_id = payment_id
    payment.date = datetime.datetime.strptime(date, "%Y-%m-%d")
    payment.amount = amount
    payment.comment = comment

    payment.due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d")
    payment.document_number = document_number or "NOP"

    try:

        db.session.commit()
        # upload_file(sale) #TODO: uplaod file

    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="danger")

    else:
        flash("Chiffre d'affaire modiffier", category="success")

    return redirect(url_for(".index_costs"))


@bp.route("/costs/remove/<int:id>", methods=["POST"])
@login_required
def remove_payment_cost(id):

    payment = db.session.query(Payments).filter(Payments.id == id).first()

    if not payment:
        flash("Le paiement n'exist pas !!!", category="warning")
        return redirect(url_for(".index_costs"))
    db.session.delete(payment)
    try:

        db.session.commit()
        flash("Paiement supprimer !!!", category="success")

    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="danger")

    return redirect(url_for(".index_costs"))
