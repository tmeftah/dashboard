from flask import render_template, request, session

from flask_login import login_required, current_user
from sqlalchemy import desc
from . import dash
from .. import db
from ..models import Companies, SalesCategories, PaymentMethod, Reconciliations
from ..utilities.utils import *


@dash.route("/dashboard")
@login_required
def dashboard():

    companies = Companies.query().all()

    return render_template(
        "dashboard/dashboard.html",
        get_sold_clients=get_sold_clients,
        get_sold_portefeuille=get_sold_portefeuille,
        get_ticket=get_ticket,
        get_impayees=get_impayees,
        get_banque=get_banque,
        get_caisse=get_caisse,
        get_stock=get_stock,
        get_costs=get_costs,
        get_purchasing=get_purchasing,
        get_payments_per_company=get_payments_per_company,
        get_payments_per_cost=get_payments_per_cost,
        get_liabilites_per_company=get_liabilites_per_company,
        get_liabilites_per_cost=get_liabilites_per_cost,
        get_debt=get_debt,
        get_debt_per_company=get_debt_per_company,
        get_debt_per_cost=get_debt_per_cost,
        get_economic_situation=get_economic_situation,
        get_financial_capacity=get_financial_capacity,
        companies=companies,
    )


@dash.route("/exploit")
@login_required
def exploit():
    salesCategories = SalesCategories.query().all()

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


@dash.route("/tresor")
def tresor():

    week = request.args.get("week")

    first_day = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())
    if week and "-W" in week:
        first_day = datetime.datetime.strptime(week + "-1", "%G-W%V-%u").date()
    else:
        iso = first_day.isocalendar()
        week = f"{iso[0]}-W{iso[1]}"

    init_sold = []
    end_sold = []

    caching = []

    debt = []

    for daynumber in range(7):
        day = first_day + datetime.timedelta(days=daynumber)
        day_befor = first_day + datetime.timedelta(days=daynumber - 1)

        query = Reconciliations.query_sum()
        query = query.filter(Reconciliations.date == day)

        init_sold.append(get_banque_on_date(end=day_befor))
        end_sold.append(get_banque_on_date(end=day))

        res_caching = []
        res_debt = []
        for payment_id in [1, 2, 3, 5, 6, 7]:
            query_caching = query.filter(
                Reconciliations.cashing == True, Reconciliations.paymentmethod_id == payment_id
            )
            query_debit = query.filter(
                Reconciliations.cashing == False, Reconciliations.paymentmethod_id == payment_id
            )
            res_caching.append(round(query_caching.scalar(), 3))
            res_debt.append(round(query_debit.scalar(), 3))

        caching.append(res_caching)
        debt.append(res_debt)

    paymentmethods = db.session.query(PaymentMethod).filter(PaymentMethod.id.notin_([7])).all()

    encaiss = (
        Reconciliations.query()
        .filter(Reconciliations.cashing == True)
        .order_by(desc(Reconciliations.date))
        .all()
    )
    decaiss = (
        Reconciliations.query()
        .filter(Reconciliations.cashing == False)
        .order_by(desc(Reconciliations.date))
        .all()
    )

    return render_template(
        "dashboard/tresor.html",
        encaiss=encaiss,
        decaiss=decaiss,
        paymentmethods=paymentmethods,
        caching=caching,
        debt=debt,
        init_sold=init_sold,
        end_sold=end_sold,
        week=week,
        first_day=first_day,
    )
