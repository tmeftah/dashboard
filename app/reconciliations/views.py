import datetime
from flask import request, render_template, flash, redirect, url_for
from flask_login import login_required
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from . import reconciliations as bp
from .. import db
from ..models import CostsDef, Reconciliations, Companies, PaymentMethod


@bp.route("/", methods=["GET"])
@login_required
def index():
    reconciliations = db.session.query(Reconciliations).order_by(desc(Reconciliations.date)).all()
    companies = db.session.query(Companies).all()
    paymentmethod = db.session.query(PaymentMethod).filter(PaymentMethod.id.notin_([4])).all()
    cosdefs = db.session.query(CostsDef).all()

    return render_template(
        "/reconciliations/index.html",
        reconciliations=reconciliations,
        paymentmethod=paymentmethod,
        companies=companies,
        cosdefs=cosdefs,
    )


@bp.route("/", methods=["POST"])
@login_required
def add_reconciliations():

    company_id = request.form.get("company_id", type=int)
    cost_id = request.form.get("cost_id", type=int)
    cashing = request.form.get("cashing", type=int)
    payment_id = request.form.get("payment_id")
    date = request.form.get("date")
    amount = request.form.get("amount")
    comment = request.form.get("comment")

    new_reconciliation = Reconciliations(
        cost_id=cost_id,
        cashing=cashing,
        company_id=company_id,
        paymentmethod_id=payment_id,
        date=datetime.datetime.strptime(date, "%Y-%m-%d"),
        amount=amount,
        comment=comment,
    )

    try:
        db.session.add(new_reconciliation)
        db.session.commit()

    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="error")

    else:
        flash("Rapprochement ajouter", category="success")

    return redirect(url_for(".index"))


@bp.route("/<int:id>", methods=["GET"])
@login_required
def get_reconciliations_by_id(id):

    reconciliation = db.session.query(Reconciliations).filter(Reconciliations.id == id).first()

    if not reconciliation:
        flash("Rapprochement n'exist pas !!!", category="warning")
        return redirect(url_for(".index"))

    companies = db.session.query(Companies).filter_by(customer=True).all()
    paymentmethod = db.session.query(PaymentMethod).filter(PaymentMethod.id.notin_([4])).all()

    return render_template(
        "/reconciliations/_id.html",
        reconciliation=reconciliation,
        companies=companies,
        paymentmethod=paymentmethod,
    )


@bp.route("/<int:id>", methods=["POST"])
@login_required
def update_reconciliations(id):

    reconciliation = db.session.query(Reconciliations).filter(Reconciliations.id == id).first()

    if not reconciliation:
        flash("Rapprochement n'exist pas !!!")
        return redirect(url_for(".index"))

    company_id = request.form.get("company_id", type=int)
    payment_id = request.form.get("payment_id", type=int)
    date = request.form.get("date")
    amount = request.form.get("amount")
    comment = request.form.get("comment")

    reconciliation.company_id = company_id
    reconciliation.paymentmethod_id = payment_id
    reconciliation.date = datetime.datetime.strptime(date, "%Y-%m-%d")
    reconciliation.amount = amount
    reconciliation.comment = comment

    try:

        db.session.commit()
        # upload_file(reconciliation)

    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="error")

    else:
        flash("Rapprochement modiffier", category="success")

    return redirect(url_for(".index"))


@bp.route("/remove/<int:id>", methods=["POST"])
@login_required
def remove_reconciliations(id):

    reconciliation = db.session.query(Reconciliations).filter(Reconciliations.id == id).first()

    if not reconciliation:
        flash("Rapprochement n'exist pas !!!", category="warning")
        return redirect(url_for(".index"))
    db.session.delete(reconciliation)
    try:

        db.session.commit()
        flash("Rapprochement supprimer !!!", category="success")

    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="danger")

    return redirect(url_for(".index"))
