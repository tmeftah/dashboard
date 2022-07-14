import datetime
from sqlalchemy.sql import func
from sqlalchemy import extract

from .. import db
from ..models import (
    Payments,
    Sales,
    Recovers,
    CostsMapping,
    Purchasing,
    Reconciliations,
    Stocks,
    CostsDef,
)


def get_sum_sales(company_id=0, pay_methode_id=0):
    query = Sales.query_sum()

    if company_id:
        query = query.filter(Sales.company_id == company_id)

    if pay_methode_id:
        query = query.filter(Sales.paymentmethod_id == pay_methode_id)

    return round(query.scalar(), 3)


def get_sum_recovers(company_id=0, pay_methode_id=0):
    query = Recovers.query_sum()

    if company_id:
        query = query.filter(Recovers.company_id == company_id)

    if pay_methode_id:
        query = query.filter(Recovers.paymentmethod_id == pay_methode_id)

    return round(query.scalar(), 3)


def get_sum_reconciliations(company_id=0, pay_methode_id=0, cashing=True):
    query = Reconciliations.query_sum().filter(Reconciliations.cashing == cashing)

    if company_id:
        query = query.filter(Reconciliations.company_id == company_id)
    else:
        query = query.filter(Reconciliations.company_id.isnot(None))

    if pay_methode_id:
        query = query.filter(Reconciliations.paymentmethod_id == pay_methode_id)

    return round(query.scalar(), 3)


def get_sum_reconciliations_costs(cost_id=0, pay_methode_id=0, cashing=True):
    query = Reconciliations.query_sum().filter(Reconciliations.cashing == cashing)

    if pay_methode_id:
        query = query.filter(Reconciliations.paymentmethod_id == pay_methode_id)

    if cost_id:
        query = query.filter(Reconciliations.cost_id == cost_id)
    else:
        query = query.filter(Reconciliations.cost_id.isnot(None))

    return round(query.scalar(), 3)


def get_sold_clients(company=0):

    sum_credits = get_sum_sales(company_id=company, pay_methode_id=4)  # credit
    sum_recovers = get_sum_recovers(company_id=company)  # all recovers
    sum_reconciliations = get_sum_reconciliations(
        company_id=company, cashing=True, pay_methode_id=7
    )

    return round(sum_credits - sum_recovers - sum_reconciliations, 3)


# TODO: Fix erro on Ticket resto
def get_sold_portefeuille(company=0, pay_methode=0):
    # le raprochement doit etre pris en compte
    sum_sales = get_sum_sales(company, pay_methode)

    sum_recovers = get_sum_recovers(company, pay_methode)

    sum_encaissements = get_sum_reconciliations(company, pay_methode, cashing=True)

    cost_and_purchasing = 0

    if pay_methode == 6:
        cost_and_purchasing = get_costs(6) + get_purchasing(pay_methode=6)

    return round(sum_sales + sum_recovers - sum_encaissements - cost_and_purchasing, 3)


def get_impayees(pay_methode=1):
    return round(0, 3)


def get_banque():
    sum_encaissements = Reconciliations.query_sum().filter(Reconciliations.cashing == True).scalar()
    sum_decaissements = (
        Reconciliations.query_sum().filter(Reconciliations.cashing == False).scalar()
    )

    return round(sum_encaissements - sum_decaissements, 3)


def get_caisse():

    sum_sales = Sales.query_sum().filter(Sales.paymentmethod_id == 1).scalar()

    sum_reconciliations = Recovers.query_sum().filter(Recovers.paymentmethod_id == 1).scalar()

    sum_cost = CostsMapping.query_sum().filter(CostsMapping.paymentmethod_id == 1).scalar()

    sum_purchasing = Purchasing.query_sum().filter(Purchasing.paymentmethod_id == 1).scalar()
    # TODO: add decaissement to the sum
    sum_decaissements = (
        Reconciliations.query_sum().filter(Reconciliations.cashing == False).scalar()
    )

    sum_decaissements = (
        Reconciliations.query_sum().filter(Reconciliations.cashing == False).scalar()
    )

    sum_encaissements_especes = (
        Reconciliations.query_sum()
        .filter(Reconciliations.cashing == True, Reconciliations.paymentmethod_id == 1)
        .scalar()
    )

    return round(
        sum_sales + sum_reconciliations - sum_cost - sum_purchasing - sum_encaissements_especes, 3
    )


def get_stock():
    today = datetime.date.today()
    res = (
        Stocks.query_sum()
        .filter(Stocks.date <= today)
        .order_by(Stocks.date.desc())
        .group_by(Stocks.date)
        .all()
    )
    if len(res) > 0:
        return round(res[0][0], 3)
    else:
        return round(0, 3)


def get_costs(cost=0, pay_methode=0):

    query = CostsMapping.query_sum()
    if pay_methode:
        query = query.filter(CostsMapping.paymentmethod_id == pay_methode)
    if cost:
        query = query.filter(CostsMapping.cost_id == cost)

    sum_cost = query.scalar()

    # sum_decaissements = get_sum_reconciliations(pay_methode_id=pay_methode, cashing=False)

    return round(sum_cost, 3)


def get_purchasing(company=0, pay_methode=0):

    query = Purchasing.query_sum()

    if company:
        query = query.filter(Purchasing.company_id == company)

    if pay_methode:
        query = query.filter(Purchasing.paymentmethod_id == pay_methode)

    sum_purchasing = query.scalar()

    return round(sum_purchasing, 3)


def get_payments_per_company(company=0, pay_methode=0):
    query = Payments.query_sum().filter(Payments.company_id.isnot(None))

    if company:
        query = query.filter(Payments.company_id == company)

    if pay_methode:
        query = query.filter(Payments.paymentmethod_id == pay_methode)

    sum_payments = query.scalar()

    return round(sum_payments, 3)


def get_payments_per_cost(cost=0, pay_methode=0):
    query = Payments.query_sum().filter(Payments.cost_id.isnot(None))

    if cost:
        query = query.filter(Payments.cost_id == cost)

    if pay_methode:
        query = query.filter(Payments.paymentmethod_id == pay_methode)

    sum_payments = query.scalar()

    return round(sum_payments, 3)


def get_liabilites_per_company(company=0, pay_methode=0):

    sum_purchasing = get_purchasing(company=company, pay_methode=pay_methode)

    # TODO: add payment
    sum_payments = get_payments_per_company(company=company, pay_methode=pay_methode)

    sum_decaissements = get_sum_reconciliations(
        company_id=company, pay_methode_id=pay_methode, cashing=False
    )

    return round(sum_purchasing + sum_payments - sum_decaissements, 3)


def get_liabilites_per_cost(cost=0, pay_methode=0):

    sum_costs = get_costs(cost == cost, pay_methode=pay_methode)

    # TODO: add payment
    sum_payments = get_payments_per_cost(cost=cost, pay_methode=pay_methode)

    sum_decaissements = get_sum_reconciliations_costs(
        cost_id=cost, pay_methode_id=pay_methode, cashing=False
    )

    return round(sum_costs + sum_payments - sum_decaissements, 3)


def get_debt_per_company(company=0):

    sum_purchasing = get_purchasing(company=company, pay_methode=4)
    sum_payments = get_payments_per_company(company=company)

    # sum_decaissements = get_sum_reconciliations(company_id=company, pay_methode_id=7, cashing=False)
    return round(sum_purchasing - sum_payments, 3)


def get_debt_per_cost(cost=0):

    sum_costs = get_costs(cost=cost, pay_methode=4)
    sum_payments = get_payments_per_cost(cost=cost)

    # sum_decaissements = get_sum_reconciliations(company_id=company, pay_methode_id=7, cashing=False)
    return round(sum_costs - sum_payments, 3)


def get_debt():
    print(get_purchasing(pay_methode=4), get_payments_per_company(), get_debt_per_company())
    return round(get_debt_per_company() + get_debt_per_cost(), 3)


def get_all_liabilities():  # tout les engagements/dettes

    sum_cost = (
        CostsMapping.query_sum()
        .filter(CostsMapping.paymentmethod_id.notin_([1, 6]))  # TODO: to be verified
        .scalar()
    )
    sum_purchasing = (
        Purchasing.query_sum()
        .filter(Purchasing.paymentmethod_id.notin_([1, 6]))  # TODO: to be verified
        .scalar()
    )

    sum_decaissements = get_sum_reconciliations(cashing=False)

    return round(sum_cost + sum_purchasing - sum_decaissements, 3)


def get_economic_situation():
    res = (
        get_sold_clients()
        + get_sold_portefeuille(pay_methode=2)
        + get_sold_portefeuille(pay_methode=3)
        + get_sold_portefeuille(pay_methode=5)
        + get_sold_portefeuille(pay_methode=6)
        + get_banque()
        + get_caisse()
        + get_stock()
        - get_all_liabilities()
    )

    return round(res, 3)


def get_financial_capacity():

    return round(get_banque() + get_caisse() - get_all_liabilities(), 3)


def get_chiffre_affaire(cum=False, pay_methode=0):
    today = datetime.date.today()
    currentMonth = datetime.datetime.now().month
    # if cum:
    #     date_ = [datetime.date.today(),datetime.date.today()]
    sale_query = Sales.query_sum()

    if cum:
        sale_query = sale_query.filter(extract("month", Sales.date) == currentMonth)
    else:
        sale_query = sale_query.filter(Sales.date == today)

    if pay_methode:

        sale_query = sale_query.filter(Sales.paymentmethod_id == pay_methode)

    sum_sales = sale_query.scalar()

    return round(sum_sales, 3)


# ********************************** exploitation ********************************


def get_sales_on_date(start=None, end=None, cum=0, today=0):
    query = Sales.query_sum()

    if cum:
        start = datetime.datetime.today().replace(day=1).date()
        query = query.filter(Sales.date >= start)
    else:
        if today:
            start = datetime.date.today()
            query = query.filter(Sales.date == start)
        else:
            if start:
                query = query.filter(Sales.date >= start)

            if end:
                query = query.filter(Sales.date <= end)

    return round(query.scalar(), 3)


def get_stock_on_date(initial=0):

    today = datetime.date.today()
    if initial:
        today = today - datetime.timedelta(days=1)

    res = (
        Stocks.query_sum()
        .filter(Stocks.date <= today)
        .order_by(Stocks.date.desc())
        .group_by(Stocks.date)
        .all()
    )
    if len(res) > 0:
        return round(res[0][0], 3)
    else:
        return round(0, 3)


def get_purchasing_on_date(start=None, end=None, cum=0, today=0):

    query = Purchasing.query_sum()

    if cum:
        start = datetime.datetime.today().replace(day=1).date()
        query = query.filter(Purchasing.date >= start)
    else:
        if today:
            start = datetime.date.today()
            query = query.filter(Purchasing.date == start)
        else:
            if start:
                query = query.filter(Purchasing.date >= start)
            if end:
                query = query.filter(Purchasing.date <= end)

    return round(query.scalar(), 3)


def get_costo_goods_sold(cum=0, today=0):
    res = (get_stock_on_date(initial=True) - get_stock_on_date()) + get_purchasing_on_date(
        cum=cum, today=today
    )
    return round(res, 3)


def get_gross_margin(cum=0, today=0):
    res = get_sales_on_date(cum=cum, today=today) - get_costo_goods_sold(cum=cum, today=today)
    return round(res, 3)


def get_costs_on_date(start=None, end=None, cum=0, today=0, fixed=0):

    query = CostsMapping.query_sum().join(CostsDef).filter(CostsDef.fixed == fixed)

    if cum:
        start = datetime.datetime.today().replace(day=1).date()
        query = query.filter(CostsMapping.date >= start)
    else:
        if today:
            start = datetime.date.today()
            query = query.filter(CostsMapping.date == start)
        else:
            if start:
                query = query.filter(CostsMapping.date >= start)
            if end:
                query = query.filter(CostsMapping.date <= end)

    return round(query.scalar(), 3)


def get_gross_operating_income(cum=0, today=0):
    res = get_gross_margin(cum=cum, today=today) - (
        get_costs_on_date(cum=cum, today=today)
        + get_costs_on_date(cum=cum, today=today, fixed=True)
    )
    return round(res, 3)


def get_tax_gross_operating_income(cum=0, today=0):
    res = 0.25 * get_gross_operating_income(cum=cum, today=today)
    return round(res, 3)


def get_net_operating_income(cum=0, today=0):
    amorti = 0
    res = (
        get_gross_operating_income(cum=cum, today=today)
        - get_tax_gross_operating_income(cum=cum, today=today)
        - amorti
    )
    return round(res, 3)


# ********************************** Tresorerie ********************************


def get_banque_on_date(start=None, end=None, today=0):
    query = Reconciliations.query_sum()

    if today:
        start = datetime.date.today()
        query = query.filter(Reconciliations.date == start)
    else:
        if start:
            query = query.filter(Reconciliations.date >= start)
        if end:
            query = query.filter(Reconciliations.date <= end)

    sum_encaissements = query.filter(Reconciliations.cashing == True).scalar()
    sum_decaissements = query.filter(Reconciliations.cashing == False).scalar()

    return round(sum_encaissements - sum_decaissements, 3)
