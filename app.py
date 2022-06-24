import os
import datetime
from dotenv import load_dotenv

from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug import exceptions

from sqlalchemy import desc
from sqlalchemy.sql import func
from sqlalchemy.exc import SQLAlchemyError
from database import db_session, init_db
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
    Payments,
)


from utils import (
    get_sold_clients,
    get_sold_portefeuille,
    get_impayees,
    get_banque,
    get_caisse,
    get_stock,
    get_costs,
    get_purchasing,
    get_liabilites,
    get_debt,
    get_economic_situation,
    get_financial_capacity,
    get_sales_on_date,
    get_stock_on_date,
    get_purchasing_on_date,
    get_costo_goods_sold,
    get_gross_margin,
    get_costs_on_date,
    get_gross_operating_income,
    get_tax_gross_operating_income,
    get_net_operating_income,
)


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


app = Flask(__name__)


if "development" == os.getenv("ENV"):
    app.config.from_object("config.DevConfig")
else:
    app.config.from_object("config.ProdConfig")


init_db(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


#
def allowed_file(filename):
    return (
        "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


def upload_file(item):
    # check if the post request has the file part
    if "foto" not in request.files:
        flash("No file part")
        return redirect(request.url)
    file = request.files["foto"]
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == "":
        # flash("No selected file") # TODO: fix zthsi flash error on empty file
        return redirect(request.url)
    if file and allowed_file(file.filename):
        format = file.filename.split(".")[-1:]
        file_name = (
            f"{'_'.join(file.filename.split('.')[:-1])}_{datetime.datetime.utcnow()}.{format}"
        )
        filename = secure_filename(file_name)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        item.document_filename = filename
        db_session.commit()


@app.errorhandler(exceptions.NotFound)
def handle_NotFound(e):
    flash("Page not found !!!")
    return redirect(url_for(".dashboard"))


@app.route("/uploads/<name>")
@login_required
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    user = db_session.query(User).get(int(user_id))
    return user


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for(".login"))


@app.before_first_request
def setup():
    pass


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

    companies = db_session.query(Companies).all()

    return render_template(
        "dashboard/dashboard.html",
        get_sold_clients=get_sold_clients,
        get_sold_portefeuille=get_sold_portefeuille,
        get_impayees=get_impayees,
        get_banque=get_banque,
        get_caisse=get_caisse,
        get_stock=get_stock,
        get_costs=get_costs,
        get_purchasing=get_purchasing,
        get_liabilites=get_liabilites,
        get_debt=get_debt,
        get_economic_situation=get_economic_situation,
        get_financial_capacity=get_financial_capacity,
        companies=companies,
    )


@app.route("/exploit")
@login_required
def exploit():
    salesCategories = db_session.query(SalesCategories).all()

    return render_template(
        "dashboard/exploit.html",
        salesCategories=salesCategories,
        get_sales_on_date=get_sales_on_date,
        get_stock_on_date=get_stock_on_date,
        get_purchasing_on_date=get_purchasing_on_date,
        get_costo_goods_sold=get_costo_goods_sold,
        get_gross_margin=get_gross_margin,
        get_costs_on_date=get_costs_on_date,
        get_gross_operating_income=get_gross_operating_income,
        get_tax_gross_operating_income=get_tax_gross_operating_income,
        get_net_operating_income=get_net_operating_income,
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


@app.route("/companies", methods=["GET"])
@login_required
def companies():
    companies = db_session.query(Companies).all()
    return render_template("companies/index.html", companies=companies)


@app.route("/companies", methods=["POST"])
@login_required
def add_companies():

    name = request.form.get("name")
    email = request.form.get("email")
    company_type = request.form.get("company_type", type=int)
    phone = request.form.get("phone")

    if company_type == 0:
        customer = True
        supplier = False

    if company_type == 1:
        customer = False
        supplier = True

    if company_type == 2:
        customer = True
        supplier = True

    new_company = Companies(
        name=name,
        email=email,
        customer=customer,
        supplier=supplier,
        phone=phone,
    )

    try:
        db_session.add(new_company)
        db_session.commit()

    except SQLAlchemyError as e:
        print(e)
        db_session.rollback()
        flash("db error", category="error")

    else:
        flash("Un nouveau Tier ajouter", category="success")

    return redirect(url_for("companies"))


# *****************************************    Sales    ****************************************************


@app.route("/sales", methods=["GET"])
@login_required
def sales():
    categorie = request.args.get("categorie", type=int, default=0)

    paymentme = request.args.get("paymentmethod", type=int, default=0)

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
        db_session.add(new_sale)
        db_session.commit()
        upload_file(new_sale)

    except SQLAlchemyError as e:
        print(e)
        db_session.rollback()
        flash("db error", category="error")

    else:
        flash("Chiffre d'affaire ajouter", category="success")

    return redirect(url_for("sales"))


@app.route("/sales/<int:id>", methods=["GET"])
@login_required
def get_sale_by_id(id):

    sale = db_session.query(Sales).filter(Sales.id == id).first()

    if not sale:
        flash("Chiffre d'affaire n'exist pas !!!")
        return redirect(url_for("sales"))

    companies = db_session.query(Companies).filter_by(customer=True).all()
    salescategories = db_session.query(SalesCategories).all()
    paymentmethod = db_session.query(PaymentMethod).filter(PaymentMethod.id.notin_([7])).all()

    return render_template(
        "/sales/_id.html",
        sale=sale,
        companies=companies,
        salescategories=salescategories,
        paymentmethod=paymentmethod,
    )


@app.route("/sales/<int:id>", methods=["POST"])
@login_required
def update_sales(id):

    sale = db_session.query(Sales).filter(Sales.id == id).first()

    if not sale:
        flash("Chiffre d'affaire n'exist pas !!!", category="warning")
        return redirect(url_for("sales"))

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

        db_session.commit()
        upload_file(sale)

    except SQLAlchemyError as e:
        print(e)
        db_session.rollback()
        flash("db error", category="danger")

    else:
        flash("Chiffre d'affaire modiffier", category="success")

    return redirect(url_for("sales"))


@app.route("/sales/remove/<int:id>", methods=["POST"])
@login_required
def remove_sales(id):

    sale = db_session.query(Sales).filter(Sales.id == id).first()

    if not sale:
        flash("Chiffre d'affaire n'exist pas !!!", category="warning")
        return redirect(url_for("sales"))
    db_session.delete(sale)
    try:

        db_session.commit()
        flash("Chiffre d'affaire supprimer !!!", category="success")

    except SQLAlchemyError as e:
        print(e)
        db_session.rollback()
        flash("db error", category="danger")

    return redirect(url_for("sales"))


@app.route("/salescategories")
@login_required
def salescategories():
    return render_template("sales/categories.html")


# *****************************************    CostsMapping    *******************************************


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
        db_session.add(new_cost)
        db_session.commit()
        upload_file(new_cost)
    except SQLAlchemyError as e:
        print(e)
        db_session.rollback()
        flash("db error", category="error")

    else:
        flash("Charge ajouter", category="success")

    return redirect(url_for("costs"))


@app.route("/costs/<int:id>", methods=["GET"])
@login_required
def get_costs_by_id(id):

    cost = db_session.query(CostsMapping).filter(CostsMapping.id == id).first()

    if not cost:
        flash("Charge n'exist pas !!!")
        return redirect(url_for("costs"))

    costsdefs = db_session.query(CostsDef).all()
    paymentmethod = db_session.query(PaymentMethod).filter(PaymentMethod.id.notin_([7])).all()

    return render_template(
        "/costs/_id.html",
        cost=cost,
        costsdefs=costsdefs,
        paymentmethod=paymentmethod,
    )


@app.route("/costs/<int:id>", methods=["POST"])
@login_required
def update_costs(id):

    cost = db_session.query(CostsMapping).filter(CostsMapping.id == id).first()

    if not cost:
        flash("La cahrge n'exist pas !!!", category="warning")
        return redirect(url_for("costs"))

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

        db_session.commit()
        upload_file(cost)

    except SQLAlchemyError as e:
        print(e)
        db_session.rollback()
        flash("db error", category="danger")

    else:
        flash("Charge modiffier", category="success")

    return redirect(url_for("costs"))


@app.route("/costs/remove/<int:id>", methods=["POST"])
@login_required
def remove_costs(id):

    cost = db_session.query(CostsMapping).filter(CostsMapping.id == id).first()

    if not cost:
        flash("La charge n'exist pas !!!", category="warning")
        return redirect(url_for("costs"))
    db_session.delete(cost)
    try:

        db_session.commit()
        flash("Charge supprimer !!!", category="success")

    except SQLAlchemyError as e:
        print(e)
        db_session.rollback()
        flash("db error", category="danger")

    return redirect(url_for("costs"))


# *****************************************    CostsDef    *******************************************


@app.route("/costs_type", methods=["POST"])
@login_required
def add_costs_type():

    fixed = request.form.get("fixed", type=int)
    name = request.form.get("name")

    new_cost_type = CostsDef(fixed=fixed, name=name)

    try:
        db_session.add(new_cost_type)
        db_session.commit()
    except SQLAlchemyError as e:
        print(e)
        db_session.rollback()
        flash("db error", category="error")

    else:
        flash("Type de Charge ajouter", category="success")

    return redirect(url_for("costs"))


# *****************************************    Purchasing    *******************************************


@app.route("/purchasings", methods=["GET"])
@login_required
def purchasings():
    print(app.config["ENV"])
    companies = db_session.query(Companies).filter_by(supplier=True).all()
    purchasings = db_session.query(Purchasing).order_by(desc(Purchasing.date)).all()
    paymentmethod = db_session.query(PaymentMethod).all()

    return render_template(
        "/purchasings/index.html",
        purchasings=purchasings,
        paymentmethod=paymentmethod,
        companies=companies,
    )


@app.route("/purchasings", methods=["POST"])
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
        db_session.add(new_purchasing)
        db_session.commit()
        upload_file(new_purchasing)
    except SQLAlchemyError as e:
        print(e)
        db_session.rollback()
        flash("db error", category="error")

    else:
        flash("Achat ajouter", category="success")

    return redirect(url_for("purchasings"))


@app.route("/purchasings/<int:id>", methods=["GET"])
@login_required
def get_purchasings_by_id(id):

    purchasing = db_session.query(Purchasing).filter(Purchasing.id == id).first()

    if not purchasing:
        flash("Achat n'exist pas !!!", category="warning")
        return redirect(url_for("purchasings"))

    companies = db_session.query(Companies).filter_by(supplier=True).all()
    salescategories = db_session.query(SalesCategories).all()
    paymentmethod = db_session.query(PaymentMethod).filter(PaymentMethod.id.notin_([7])).all()

    return render_template(
        "/purchasings/_id.html",
        purchasing=purchasing,
        companies=companies,
        salescategories=salescategories,
        paymentmethod=paymentmethod,
    )


@app.route("/purchasings/<int:id>", methods=["POST"])
@login_required
def update_purchasings(id):

    purchasing = db_session.query(Purchasing).filter(Purchasing.id == id).first()

    if not purchasing:
        flash("Achat n'exist pas !!!")
        return redirect(url_for("purchasings"))

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

        db_session.commit()
        upload_file(purchasing)

    except SQLAlchemyError as e:
        print(e)
        db_session.rollback()
        flash("db error", category="error")

    else:
        flash("Achat modiffier", category="success")

    return redirect(url_for("purchasings"))


@app.route("/purchasings/remove/<int:id>", methods=["POST"])
@login_required
def remove_purchasings(id):

    purchasing = db_session.query(Purchasing).filter(Purchasing.id == id).first()

    if not purchasing:
        flash("Achat n'exist pas !!!", category="warning")
        return redirect(url_for("purchasings"))
    db_session.delete(purchasing)
    try:

        db_session.commit()
        flash("Achat supprimer !!!", category="success")

    except SQLAlchemyError as e:
        print(e)
        db_session.rollback()
        flash("db error", category="danger")

    return redirect(url_for("purchasings"))


# *****************************************    Recovers    *******************************************


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
    payment_id = request.form.get("payment_id", type=int)
    date = request.form.get("date")
    amount = request.form.get("amount")
    comment = request.form.get("comment")

    document_number = request.form.get("document_number")
    due_date = request.form.get("due_date")

    new_recover = Recovers(
        # categorie_id=categorie_id,
        company_id=company_id,
        paymentmethod_id=payment_id,
        date=datetime.datetime.strptime(date, "%Y-%m-%d"),
        amount=amount,
        comment=comment,
    )

    if payment_id in [2, 3]:
        new_recover.due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d")
        new_recover.document_number = document_number

    try:
        db_session.add(new_recover)
        db_session.commit()
        upload_file(new_recover)
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
    payments = db_session.query(Payments).order_by(desc(Payments.date)).all()
    suppliers = db_session.query(Companies).filter_by(supplier=True).all()
    cost_defs = db_session.query(CostsDef).all()

    paymentmethod = (
        db_session.query(PaymentMethod).filter(PaymentMethod.name.not_like("Credit")).all()
    )

    return render_template(
        "/payments/index.html",
        payments=payments,
        paymentmethod=paymentmethod,
        suppliers=suppliers,
        cost_defs=cost_defs,
        get_sold_clients=get_sold_clients,
    )


@app.route("/payments", methods=["POST"])
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
        db_session.add(new_payment)
        db_session.commit()
        upload_file(new_payment)
    except SQLAlchemyError as e:
        print(e)
        db_session.rollback()
        flash("db error", category="error")

    else:
        flash("Payment ajouter", category="success")

    return redirect(url_for("payments"))


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
    from datetime import datetime, date

    def today():
        return date.today()

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
        today=today,
    )


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == "__main__":
    app.run(host="0.0.0.0")
