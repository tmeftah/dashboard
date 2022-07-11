import datetime
from flask import request, render_template, flash, redirect, url_for
from flask_login import login_required
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from . import stocks as bp
from .. import db
from ..models import Stocks


@bp.route("/", methods=["GET"])
@login_required
def index():
    stocks = Stocks.query().order_by(desc(Stocks.date)).all()

    return render_template(
        "/stocks/index.html",
        stocks=stocks,
    )


@bp.route("/", methods=["POST"])
@login_required
def add_stocks():

    amount = request.form.get("amount")
    date = request.form.get("date")
    comment = request.form.get("comment")

    new_stock = Stocks(
        amount=amount,
        date=datetime.datetime.strptime(date, "%Y-%m-%d"),
        comment=comment,
    )

    try:
        db.session.add(new_stock)
        db.session.commit()
    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="danger")

    else:
        flash("Stock ajouter", category="success")

    return redirect(url_for(".index"))


@bp.route("/<int:id>", methods=["GET"])
@login_required
def get_stocks_by_id(id):

    stock = Stocks.query().filter(Stocks.id == id).first()

    if not stock:
        flash("Stock n'exist pas !!!", category="warning")
        return redirect(url_for(".index"))

    return render_template(
        "/stocks/_id.html",
        stock=stock,
    )


@bp.route("/<int:id>", methods=["POST"])
@login_required
def update_stocks(id):

    stock = Stocks.query().filter(Stocks.id == id).first()

    if not stock:
        flash("Stock n'exist pas !!!", category="warning")
        return redirect(url_for(".index"))

    date = request.form.get("date")
    amount = request.form.get("amount")
    comment = request.form.get("comment")

    stock.date = datetime.datetime.strptime(date, "%Y-%m-%d")
    stock.amount = amount
    stock.comment = comment

    try:

        db.session.commit()

    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="danger")

    else:
        flash("Stock modiffier", category="success")

    return redirect(url_for(".index"))


@bp.route("/remove/<int:id>", methods=["POST"])
@login_required
def remove_stocks(id):

    stock = Stocks.query().filter(Stocks.id == id).first()

    if not stock:
        flash("Stock n'exist pas !!!", category="warning")
        return redirect(url_for(".index"))
    db.session.delete(stock)
    try:

        db.session.commit()
        flash("Stock supprimer !!!", category="success")

    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash("db error", category="danger")

    return redirect(url_for(".index"))
