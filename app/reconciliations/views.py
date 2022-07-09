import datetime
from flask import request, render_template, flash, redirect, url_for
from flask_login import login_required
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from . import reconciliations as bp
from .. import db
from ..models import CostsDef, Reconciliations, Companies, PaymentMethod
from ..utilities.utils2 import toDate, compare


@bp.route("/", methods=["GET"])
@login_required
def index():

    s_categorie = request.args.get("s_categorie", type=int, default=0)
    s_type = request.args.get("s_type", type=int, default=0)

    s_company = request.args.get("s_company", type=int, default=0)
    s_costdef = request.args.get("s_costdef", type=int, default=0)
    s_paymentmethod = request.args.get("s_paymentmethod", type=int, default=0)
    s_op = request.args.get("s_op", type=str, default="")
    s_amount = request.args.get("s_amount", type=float, default=0.0)
    s_start_date = request.args.get("s_start_date", type=toDate, default="")
    s_end_date = request.args.get("s_end_date", type=toDate, default="")

    query = db.session.query(Reconciliations)
    if s_categorie == 1:
        query = query.join(Companies).filter(Companies.customer == True)
        if s_company > 0:
            query = query.filter(Reconciliations.company_id == s_company)

    if s_categorie == 2:
        query = query.join(Companies).filter(Companies.supplier == True)
        if s_company > 0:
            query = query.filter(Reconciliations.company_id == s_company)

    if s_categorie == 3:
        query = query.filter(Reconciliations.company_id == None)
        if s_costdef > 0:
            query = query.filter(Reconciliations.cost_id == s_costdef)

    if s_type == 1:
        query = query.filter(Reconciliations.cashing == True)
    if s_type == 2:
        query = query.filter(Reconciliations.cashing == False)

    if s_paymentmethod > 0:
        query = query.filter(Reconciliations.paymentmethod_id == s_paymentmethod)

    if s_op in ["big", "small", "equal"]:
        if s_amount >= 0:
            query = query.filter(compare(Reconciliations.amount, s_amount, s_op))

    if s_start_date:
        query = query.filter(Reconciliations.date >= s_start_date)
    if s_end_date:
        query = query.filter(Reconciliations.date <= s_end_date)

    reconciliations = query.order_by(desc(Reconciliations.date)).all()

    companies = db.session.query(Companies).all()
    paymentmethod = db.session.query(PaymentMethod).filter(PaymentMethod.id.notin_([4])).all()
    cosdefs = db.session.query(CostsDef).all()

    return render_template(
        "/reconciliations/index.html",
        reconciliations=reconciliations,
        paymentmethod=paymentmethod,
        companies=companies,
        cosdefs=cosdefs,
        s_categorie=s_categorie,
        s_type=s_type,
        s_company=s_company,
        s_costdef=s_costdef,
        s_paymentmethod=s_paymentmethod,
        s_op=s_op,
        s_amount=s_amount,
        s_start_date=s_start_date,
        s_end_date=s_end_date,
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
