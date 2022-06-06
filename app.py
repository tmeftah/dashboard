from xmlrpc.client import boolean
from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import desc
from sqlalchemy.orm import scoped_session
from sqlalchemy.exc import SQLAlchemyError
from database import db_session, engine, init_db
from models import (
    Recovers,
    Sales,
    SalesCategories,
    PaymentMethod,
    Companies,
    CostsDef,
    CostsMapping,
    Purchasing,
    Rapprochements,
    Stocks,
)
from utils import (
    get_sold_client,
    get_sold_portefeuille,
    get_impayees,
    get_banque,
    get_caisse,
    get_stock,
    get_engagements,
)
import datetime

# models.Base.metadata.create_all(bind=engine)

app = Flask(__name__)
app.secret_key = "super secret key"


@app.before_first_request
def setup():
    init_db()


@app.route("/")
def index():
    return render_template("about.html")


@app.route("/dashboard")
def dashboard():

    return render_template(
        "dashboard/dashboard.html",
        get_sold_client=get_sold_client,
        get_sold_portefeuille=get_sold_portefeuille,
        get_impayees=get_impayees,
        get_banque=get_banque,
        get_caisse=get_caisse,
        get_stock=get_stock,
        get_engagements=get_engagements,
    )


@app.route("/exploit")
def exploit():

    return render_template("dashboard/exploit.html")


@app.route("/tresor")
def tresor():

    return render_template("dashboard/tresor.html")


@app.route("/companies")
def companies():
    companies = db_session.query(Companies).all()
    return render_template("companies/index.html", companies=companies)


@app.route("/sales", methods=["GET"])
def sales():
    sales = db_session.query(Sales).order_by(desc(Sales.date)).all()
    companies = db_session.query(Companies).filter_by(customer=True).all()
    salescategories = db_session.query(SalesCategories).all()
    paymentmethod = db_session.query(PaymentMethod).all()

    return render_template(
        "/sales/index.html",
        sales=sales,
        companies=companies,
        salescategories=salescategories,
        paymentmethod=paymentmethod,
    )


@app.route("/sales", methods=["POST"])
def add_sales():
    categorie_id = request.form.get("categorie_id")
    company_id = request.form.get("company_id")
    payment_id = request.form.get("payment_id")
    date = request.form.get("date")
    amount = request.form.get("amount")
    comment = request.form.get("comment")

    new_sale = Sales(
        categorie_id=categorie_id,
        company_id=company_id,
        paymentmethod_id=payment_id,
        date=datetime.datetime.strptime(date, "%Y-%m-%d"),
        amount=amount,
        comment=comment,
    )

    try:
        db_session.add(new_sale)
        db_session.commit()
    except SQLAlchemyError as e:
        print(e)
        db_session.rollback()
        flash("db error", category="error")

    else:
        flash("Chiffre d'affaire ajouter", category="success")

    return redirect(url_for("sales"))


@app.route("/salescategories")
def salescategories():
    return render_template("sales/categories.html")


@app.route("/costs", methods=["GET"])
def costs():
    costsmappings = db_session.query(CostsMapping).order_by(desc(CostsMapping.date)).all()
    costsdefs = db_session.query(CostsDef).all()
    paymentmethod = db_session.query(PaymentMethod).all()

    return render_template(
        "/costs/index.html",
        costsmappings=costsmappings,
        costsdefs=costsdefs,
        paymentmethod=paymentmethod,
    )


@app.route("/costs", methods=["POST"])
def add_costs():

    cost_id = request.form.get("cost_id")
    payment_id = request.form.get("payment_id")
    date = request.form.get("date")
    amount = request.form.get("amount")
    comment = request.form.get("comment")

    new_cost = CostsMapping(
        cost_id=cost_id,
        paymentmethod_id=payment_id,
        date=datetime.datetime.strptime(date, "%Y-%m-%d"),
        amount=amount,
        comment=comment,
    )

    try:
        db_session.add(new_cost)
        db_session.commit()
    except SQLAlchemyError as e:
        print(e)
        db_session.rollback()
        flash("db error", category="error")

    else:
        flash("Charge ajouter", category="success")

    return redirect(url_for("costs"))


@app.route("/purchasings", methods=["GET"])
def purchasings():
    purchasings = db_session.query(Purchasing).order_by(desc(Purchasing.date)).all()

    paymentmethod = db_session.query(PaymentMethod).all()

    return render_template(
        "/purchasing/index.html",
        purchasings=purchasings,
        paymentmethod=paymentmethod,
    )


@app.route("/purchasings", methods=["POST"])
def add_purchasings():

    payment_id = request.form.get("payment_id")
    date = request.form.get("date")
    amount = request.form.get("amount")
    comment = request.form.get("comment")

    new_purchasing = Purchasing(
        paymentmethod_id=payment_id,
        date=datetime.datetime.strptime(date, "%Y-%m-%d"),
        amount=amount,
        comment=comment,
    )

    try:
        db_session.add(new_purchasing)
        db_session.commit()
    except SQLAlchemyError as e:
        print(e)
        db_session.rollback()
        flash("db error", category="error")

    else:
        flash("Achat ajouter", category="success")

    return redirect(url_for("purchasings"))


@app.route("/recovers", methods=["GET"])
def recovers():
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
    )


@app.route("/rapprochements", methods=["GET"])
def rapprochements():
    rapprochements = db_session.query(Rapprochements).order_by(desc(Rapprochements.date)).all()
    companies = db_session.query(Companies).all()
    paymentmethod = db_session.query(PaymentMethod).filter(PaymentMethod.id.in_([2, 3])).all()

    return render_template(
        "/rapprochements/index.html",
        rapprochements=rapprochements,
        paymentmethod=paymentmethod,
        companies=companies,
    )


@app.route("/rapprochements", methods=["POST"])
def add_rapprochements():
    categorie_id = request.form.get("categorie_id", type=int)
    company_id = request.form.get("company_id", type=int)
    cashing = request.form.get("cashing", type=int)
    payment_id = request.form.get("payment_id")
    date = request.form.get("date")
    amount = request.form.get("amount")
    comment = request.form.get("comment")

    new_rapprochement = Rapprochements(
        # categorie_id=categorie_id,
        cashing=cashing,
        company_id=company_id,
        paymentmethod_id=payment_id,
        date=datetime.datetime.strptime(date, "%Y-%m-%d"),
        amount=amount,
        comment=comment,
    )

    try:
        db_session.add(new_rapprochement)
        db_session.commit()
    except SQLAlchemyError as e:
        print(e)
        db_session.rollback()
        flash("db error", category="error")

    else:
        flash("Rapprochement ajouter", category="success")

    return redirect(url_for("rapprochements"))


@app.route("/stocks", methods=["GET"])
def stocks():
    stocks = db_session.query(Stocks).order_by(desc(Stocks.date)).all()

    return render_template(
        "/stocks/index.html",
        stocks=stocks,
    )


@app.route("/stocks", methods=["POST"])
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
        db_session.add(new_stock)
        db_session.commit()
    except SQLAlchemyError as e:
        print(e)
        db_session.rollback()
        flash("db error", category="error")

    else:
        flash("Stock ajouter", category="success")

    return redirect(url_for("stocks"))


@app.context_processor
def utility_processor():
    import calendar
    from calendar import Calendar, monthrange
    from datetime import datetime

    def toDate(year, month, day):
        return datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d").date()

    def format_price(amount, currency="€"):
        return "{0:.2f}{1}".format(amount, currency)

    def get_months():
        return list(calendar.month_name)

    def get_monthdates(year, month):
        obj = calendar.Calendar()
        li = []

        # iterating with itermonthdates
        for day in obj.itermonthdates(year, month):
            li.append(day)
        return li

    def get_monthdays_with_name(year, month):
        l = []
        for i in range(monthrange(year, month)[1]):
            l.append(
                {"number": i + 1, "name": calendar.day_name[calendar.weekday(year, month, i + 1)]}
            )
        return l

    return dict(
        format_price=format_price,
        get_months=get_months,
        get_monthdates=get_monthdates,
        get_monthdays_with_name=get_monthdays_with_name,
        toDate=toDate,
    )


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
