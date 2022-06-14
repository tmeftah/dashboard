from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import desc
from sqlalchemy.orm import scoped_session
from sqlalchemy.exc import SQLAlchemyError
from database import db_session, engine, init_db
from models import (
    User,
    Recovers,
    Sales,
    SalesCategories,
    PaymentMethod,
    Companies,
    CostsDef,
    CostsMapping,
    Purchasing,
    Reconciliations,
    Stocks,
)
from utils import (
    get_sold_clients,
    get_sold_portefeuille,
    get_impayees,
    get_banque,
    get_caisse,
    get_stock,
    get_engagements,
    get_chiffre_affaire,
)
import datetime

# models.Base.metadata.create_all(bind=engine)

app = Flask(__name__)
app.secret_key = "super secret key"

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    user = db_session.query(User).get(int(user_id))
    print(user)
    return user


@app.before_first_request
def setup():
    init_db()


@app.route("/sw.js")
def sw():
    return app.send_static_file("sw.js")


@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():

    email = request.form.get("email")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False

    user = db_session.query(User).filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash("Please check your login details and try again.")
        return redirect(
            url_for("login")
        )  # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for("dashboard"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    return render_template("about.html")


@app.route("/dashboard")
@login_required
def dashboard():

    companies = db_session.query(Companies).filter(Companies.customer == True).all()

    return render_template(
        "dashboard/dashboard.html",
        get_sold_clients=get_sold_clients,
        get_sold_portefeuille=get_sold_portefeuille,
        get_impayees=get_impayees,
        get_banque=get_banque,
        get_caisse=get_caisse,
        get_stock=get_stock,
        get_engagements=get_engagements,
        companies=companies,
    )


@app.route("/exploit")
@login_required
def exploit():
    salesCategories = db_session.query(SalesCategories).all()

    return render_template(
        "dashboard/exploit.html",
        salesCategories=salesCategories,
        get_chiffre_affaire=get_chiffre_affaire,
    )


@app.route("/tresor")
def tresor():
    paymentmethods = db_session.query(PaymentMethod).filter(PaymentMethod.id.notin_([7])).all()

    encaiss = (
        db_session.query(Reconciliations)
        .filter(Reconciliations.cashing == True)
        .order_by(desc(Reconciliations.date))
        .all()
    )
    decaiss = (
        db_session.query(Reconciliations)
        .filter(Reconciliations.cashing == False)
        .order_by(desc(Reconciliations.date))
        .all()
    )

    return render_template(
        "dashboard/tresor.html", encaiss=encaiss, decaiss=decaiss, paymentmethods=paymentmethods
    )


@app.route("/companies")
@login_required
def companies():
    companies = db_session.query(Companies).all()
    return render_template("companies/index.html", companies=companies)


@app.route("/sales", methods=["GET"])
@login_required
def sales():
    categorie = request.args.get("categorie", type=int, default=0)

    paymentme = request.args.get("paymentmethod", type=int, default=0)
    print(categorie)
    print(paymentme)

    query = db_session.query(Sales)

    if categorie:
        query = query.filter(Sales.categorie_id == categorie)

    if paymentme:
        query = query.filter(Sales.paymentmethod_id == paymentme)

    sales = query.order_by(desc(Sales.date)).all()

    companies = db_session.query(Companies).filter_by(customer=True).all()
    salescategories = db_session.query(SalesCategories).all()
    paymentmethod = db_session.query(PaymentMethod).filter(PaymentMethod.id.notin_([7])).all()

    return render_template(
        "/sales/index.html",
        sales=sales,
        companies=companies,
        salescategories=salescategories,
        paymentmethod=paymentmethod,
    )


@app.route("/sales", methods=["POST"])
@login_required
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
@login_required
def salescategories():
    return render_template("sales/categories.html")


@app.route("/costs", methods=["GET"])
@login_required
def costs():
    costsmappings = db_session.query(CostsMapping).order_by(desc(CostsMapping.date)).all()
    costsdefs = db_session.query(CostsDef).all()
    paymentmethod = db_session.query(PaymentMethod).filter(PaymentMethod.id.notin_([7])).all()

    return render_template(
        "/costs/index.html",
        costsmappings=costsmappings,
        costsdefs=costsdefs,
        paymentmethod=paymentmethod,
    )


@app.route("/costs", methods=["POST"])
@login_required
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
@login_required
def purchasings():
    purchasings = db_session.query(Purchasing).order_by(desc(Purchasing.date)).all()

    paymentmethod = db_session.query(PaymentMethod).all()

    return render_template(
        "/purchasing/index.html",
        purchasings=purchasings,
        paymentmethod=paymentmethod,
    )


@app.route("/purchasings", methods=["POST"])
@login_required
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
@login_required
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
        get_sold_clients=get_sold_clients,
    )


@app.route("/recovers", methods=["POST"])
@login_required
def add_recovers():
    categorie_id = request.form.get("categorie_id", type=int)
    company_id = request.form.get("company_id", type=int)
    payment_id = request.form.get("payment_id")
    date = request.form.get("date")
    amount = request.form.get("amount")
    comment = request.form.get("comment")

    new_recover = Recovers(
        # categorie_id=categorie_id,
        company_id=company_id,
        paymentmethod_id=payment_id,
        date=datetime.datetime.strptime(date, "%Y-%m-%d"),
        amount=amount,
        comment=comment,
    )

    try:
        db_session.add(new_recover)
        db_session.commit()
    except SQLAlchemyError as e:
        print(e)
        db_session.rollback()
        flash("db error", category="error")

    else:
        flash("Recovers ajouter", category="success")

    return redirect(url_for("recovers"))


@app.route("/payments", methods=["GET"])
@login_required
def payments():
    recovers = db_session.query(Recovers).order_by(desc(Recovers.date)).all()
    companies = db_session.query(Companies).filter_by(customer=True).all()

    paymentmethod = (
        db_session.query(PaymentMethod).filter(PaymentMethod.name.not_like("Credit")).all()
    )

    return render_template(
        "/payments/index.html",
        recovers=recovers,
        paymentmethod=paymentmethod,
        companies=companies,
        get_sold_clients=get_sold_clients,
    )


@app.route("/payments", methods=["POST"])
@login_required
def add_payments():
    categorie_id = request.form.get("categorie_id", type=int)
    company_id = request.form.get("company_id", type=int)
    payment_id = request.form.get("payment_id")
    date = request.form.get("date")
    amount = request.form.get("amount")
    comment = request.form.get("comment")

    new_payment = Recovers(
        # categorie_id=categorie_id,
        company_id=company_id,
        paymentmethod_id=payment_id,
        date=datetime.datetime.strptime(date, "%Y-%m-%d"),
        amount=amount,
        comment=comment,
    )

    try:
        db_session.add(new_payment)
        db_session.commit()
    except SQLAlchemyError as e:
        print(e)
        db_session.rollback()
        flash("db error", category="error")

    else:
        flash("Recovers ajouter", category="success")

    return redirect(url_for("recovers"))


@app.route("/reconciliations", methods=["GET"])
@login_required
def reconciliations():
    reconciliations = db_session.query(Reconciliations).order_by(desc(Reconciliations.date)).all()
    companies = db_session.query(Companies).all()
    paymentmethod = db_session.query(PaymentMethod).filter(PaymentMethod.id.notin_([4])).all()

    return render_template(
        "/reconciliations/index.html",
        reconciliations=reconciliations,
        paymentmethod=paymentmethod,
        companies=companies,
    )


@app.route("/reconciliations", methods=["POST"])
@login_required
def add_reconciliations():
    categorie_id = request.form.get("categorie_id", type=int)
    company_id = request.form.get("company_id", type=int)
    cashing = request.form.get("cashing", type=int)
    payment_id = request.form.get("payment_id")
    date = request.form.get("date")
    amount = request.form.get("amount")
    comment = request.form.get("comment")

    new_reconciliation = Reconciliations(
        # categorie_id=categorie_id,
        cashing=cashing,
        company_id=company_id,
        paymentmethod_id=payment_id,
        date=datetime.datetime.strptime(date, "%Y-%m-%d"),
        amount=amount,
        comment=comment,
    )

    try:
        db_session.add(new_reconciliation)
        db_session.commit()
    except SQLAlchemyError as e:
        print(e)
        db_session.rollback()
        flash("db error", category="error")

    else:
        flash("Rapprochement ajouter", category="success")

    return redirect(url_for("reconciliations"))


@app.route("/stocks", methods=["GET"])
@login_required
def stocks():
    stocks = db_session.query(Stocks).order_by(desc(Stocks.date)).all()

    return render_template(
        "/stocks/index.html",
        stocks=stocks,
    )


@app.route("/stocks", methods=["POST"])
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
