import datetime
from flask import request, render_template, flash, redirect, url_for
from flask_login import login_required
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from . import payments as bp
from .. import db
from ..models import Payments, Companies, PaymentMethod, CostsDef


@bp.route("/", methods=["GET"])
@login_required
def index():
    payments = db.session.query(Payments).order_by(desc(Payments.date)).all()
    suppliers = db.session.query(Companies).filter_by(supplier=True).all()
    cost_defs = db.session.query(CostsDef).all()

    paymentmethod = (
        db.session.query(PaymentMethod).filter(PaymentMethod.name.not_like("Credit")).all()
    )

    return render_template(
        "/payments/index.html",
        payments=payments,
        paymentmethod=paymentmethod,
        suppliers=suppliers,
        cost_defs=cost_defs,
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

    return redirect(url_for(".index"))
