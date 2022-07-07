import datetime
from flask import request, render_template, flash, redirect, url_for
from flask_login import login_required
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from . import costs as bp
from .. import db
from ..models import CostsMapping, CostsDef, PaymentMethod


@bp.route("/", methods=["GET"])
@login_required
def index():
    costsmappings = db.session.query(CostsMapping).order_by(desc(CostsMapping.date)).all()
    costsdefs = db.session.query(CostsDef).all()
    paymentmethod = db.session.query(PaymentMethod).filter(PaymentMethod.id.notin_([7])).all()

    return render_template(
        "/costs/index.html",
        costsmappings=costsmappings,
        costsdefs=costsdefs,
        paymentmethod=paymentmethod,
    )


@bp.route("/", methods=["POST"])
@login_required
def add_costs():

    cost_id = request.form.get("cost_id", type=int)
    payment_id = request.form.get("payment_id", type=int)
    date = request.form.get("date")
    amount = request.form.get("amount")
    comment = request.form.get("comment")

    document_number = request.form.get("document_number")
    due_date = request.form.get("due_date")

    new_cost = CostsMapping(
        cost_id=cost_id,
        paymentmethod_id=payment_id,
        date=datetime.datetime.strptime(date, "%Y-%m-%d"),
        amount=amount,
        comment=comment,
    )

    if payment_id in [2, 3]:
        new_cost.due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d")
        new_cost.document_number = document_number

    try:
        db.session.add(new_cost)
        db.session.commit()
        # upload_file(new_cost) # TODO:upload
    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="error")

    else:
        flash("Charge ajouter", category="success")

    return redirect(url_for(".index"))


@bp.route("/<int:id>", methods=["GET"])
@login_required
def get_costs_by_id(id):

    cost = db.session.query(CostsMapping).filter(CostsMapping.id == id).first()

    if not cost:
        flash("Charge n'exist pas !!!")
        return redirect(url_for(".index"))

    costsdefs = db.session.query(CostsDef).all()
    paymentmethod = db.session.query(PaymentMethod).filter(PaymentMethod.id.notin_([7])).all()

    return render_template(
        "/costs/_id.html",
        cost=cost,
        costsdefs=costsdefs,
        paymentmethod=paymentmethod,
    )


@bp.route("/<int:id>", methods=["POST"])
@login_required
def update_costs(id):

    cost = db.session.query(CostsMapping).filter(CostsMapping.id == id).first()

    if not cost:
        flash("La cahrge n'exist pas !!!", category="warning")
        return redirect(url_for(".index"))

    cost_id = request.form.get("cost_id", type=int)
    payment_id = request.form.get("payment_id", type=int)
    date = request.form.get("date")
    amount = request.form.get("amount")
    comment = request.form.get("comment")

    document_number = request.form.get("document_number")
    due_date = request.form.get("due_date")

    cost.cost_id = cost_id
    cost.paymentmethod_id = payment_id
    cost.date = datetime.datetime.strptime(date, "%Y-%m-%d")
    cost.amount = amount
    cost.comment = comment

    cost.due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d")
    cost.document_number = document_number or "NOP"

    try:

        db.session.commit()
        # upload_file(cost) # TODO:upload

    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="danger")

    else:
        flash("Charge modiffier", category="success")

    return redirect(url_for(".index"))


@bp.route("/remove/<int:id>", methods=["POST"])
@login_required
def remove_costs(id):

    cost = db.session.query(CostsMapping).filter(CostsMapping.id == id).first()

    if not cost:
        flash("La charge n'exist pas !!!", category="warning")
        return redirect(url_for(".index"))
    db.session.delete(cost)
    try:

        db.session.commit()
        flash("Charge supprimer !!!", category="success")

    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="danger")

    return redirect(url_for(".index"))


# *****************************************    CostsDef    *******************************************


@bp.route("/costs_type", methods=["POST"])
@login_required
def add_costs_type():

    fixed = request.form.get("fixed", type=int)
    name = request.form.get("name")

    new_cost_type = CostsDef(fixed=fixed, name=name)

    try:
        db.session.add(new_cost_type)
        db.session.commit()
    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="error")

    else:
        flash("Type de Charge ajouter", category="success")

    return redirect(url_for(".index"))
