from database import db_session
from sqlalchemy.sql import func
from sqlalchemy import extract
from models import Sales, Recovers, CostsMapping, Purchasing, Reconciliations, Stocks
import datetime


def get_sum_sales(company_id=0, pay_methode_id=0):
    query = db_session.query(func.coalesce(func.sum(Sales.amount), 0))

    if company_id:
        query = query.filter(Sales.company_id == company_id)

    if pay_methode_id:
        query = query.filter(Sales.paymentmethod_id == pay_methode_id)

    return query.scalar()


def get_sum_recovers(company_id=0, pay_methode_id=0):
    query = db_session.query(func.coalesce(func.sum(Recovers.amount), 0))

    if company_id:
        query = query.filter(Recovers.company_id == company_id)

    if pay_methode_id:
        query = query.filter(Recovers.paymentmethod_id == pay_methode_id)

    return query.scalar()


def get_sum_reconciliations(company_id=0, pay_methode_id=0, cashing=True):
    query = db_session.query(func.coalesce(func.sum(Reconciliations.amount), 0)).filter(
        Reconciliations.cashing == cashing
    )

    if company_id:
        query = query.filter(Reconciliations.company_id == company_id)

    if pay_methode_id:
        query = query.filter(Reconciliations.paymentmethod_id == pay_methode_id)

    return query.scalar()


def get_sold_clients(company=0):

    sum_credits = get_sum_sales(company_id=company, pay_methode_id=4)  # credit
    sum_recovers = get_sum_recovers(company_id=company)  # all recovers

    return sum_credits - sum_recovers


def get_sold_portefeuille(company=0, pay_methode=0):
    # le raprochement doit etre pris en compte
    sum_sales = get_sum_sales(company, pay_methode)

    sum_recovers = get_sum_recovers(company, pay_methode)

    sum_encaissements = get_sum_reconciliations(company, pay_methode, cashing=True)

    cost_and_purchasing = 0

    if pay_methode == 6:
        cost_and_purchasing = get_costs(6) + get_purchasing(pay_methode=6)

    return sum_sales + sum_recovers - sum_encaissements - cost_and_purchasing


def get_impayees(pay_methode=1):
    return 0


def get_banque():
    sum_encaissements = (
        db_session.query(func.coalesce(func.sum(Reconciliations.amount), 0))
        .filter(Reconciliations.cashing == True)
        .scalar()
    )
    sum_decaissements = (
        db_session.query(func.coalesce(func.sum(Reconciliations.amount), 0))
        .filter(Reconciliations.cashing == False)
        .scalar()
    )
    return sum_encaissements - sum_decaissements


def get_caisse():

    sum_sales = (
        db_session.query(func.coalesce(func.sum(Sales.amount), 0))
        .filter(Sales.paymentmethod_id == 1)
        .scalar()
    )

    sum_reconciliations = (
        db_session.query(func.coalesce(func.sum(Recovers.amount), 0))
        .filter(Recovers.paymentmethod_id == 1)
        .scalar()
    )

    sum_cost = (
        db_session.query(func.coalesce(func.sum(CostsMapping.amount), 0))
        .filter(CostsMapping.paymentmethod_id == 1)
        .scalar()
    )

    sum_purchasing = (
        db_session.query(func.coalesce(func.sum(Purchasing.amount), 0))
        .filter(Purchasing.paymentmethod_id == 1)
        .scalar()
    )
    # TODO: add decaissement to the sum
    sum_decaissements = (
        db_session.query(func.coalesce(func.sum(Reconciliations.amount), 0))
        .filter(Reconciliations.cashing == False)
        .scalar()
    )

    return sum_sales + sum_reconciliations - sum_cost - sum_purchasing


def get_stock():
    today = datetime.date.today()
    res = (
        db_session.query(func.coalesce(func.sum(Stocks.amount), 0))
        .filter(Stocks.date <= today)
        .order_by(Stocks.date.desc())
        .group_by(Stocks.date)
        .all()
    )
    if len(res) > 0:
        return res[0][0]
    else:
        return 0


def get_costs(pay_methode=0):

    query = db_session.query(func.coalesce(func.sum(CostsMapping.amount), 0))
    if pay_methode:
        query = query.filter(CostsMapping.paymentmethod_id == pay_methode)

    sum_cost = query.scalar()

    # sum_decaissements = get_sum_reconciliations(pay_methode_id=pay_methode, cashing=False)

    return sum_cost


def get_purchasing(company=0, pay_methode=0):

    query = db_session.query(func.coalesce(func.sum(Purchasing.amount), 0))

    if company:
        query = query.filter(Purchasing.company_id == company)

    if pay_methode:
        query = query.filter(Purchasing.paymentmethod_id == pay_methode)

    sum_purchasing = query.scalar()

    sum_decaissements = get_sum_reconciliations(
        company_id=company, pay_methode_id=pay_methode, cashing=False
    )

    return sum_purchasing - sum_decaissements


def get_liabilites(company=0, pay_methode=0):
    sum_purchasing = 0
    sum_cost = 0

    sum_purchasing = get_purchasing(company_id=company, pay_methode=pay_methode)

    sum_cost = get_costs(pay_methode=pay_methode)

    sum_decaissements = get_sum_reconciliations(
        company_id=company, pay_methode_id=pay_methode, cashing=False
    )
    return sum_purchasing + sum_cost - sum_decaissements


def get_debt(company=0):

    sum_purchasing = get_purchasing(company_id=company, pay_methode=4)
    sum_cost = get_costs(pay_methode=4)

    sum_decaissements = get_sum_reconciliations(company_id=company, pay_methode_id=7, cashing=False)
    return sum_purchasing + sum_cost - sum_decaissements


def get_all_liabilities():  # tout les engagements/dettes

    sum_cost = (
        db_session.query(func.coalesce(func.sum(CostsMapping.amount), 0))
        .filter(CostsMapping.paymentmethod_id.notin_([1, 6]))  # TODO: to be verified
        .scalar()
    )
    sum_purchasing = (
        db_session.query(func.coalesce(func.sum(Purchasing.amount), 0))
        .filter(Purchasing.paymentmethod_id.notin_([1, 6]))  # TODO: to be verified
        .scalar()
    )

    sum_decaissements = get_sum_reconciliations(cashing=False)

    return sum_cost + sum_purchasing - sum_decaissements


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

    return res


def get_financial_capacity():

    return get_banque() + get_caisse() - get_all_liabilities()


def get_chiffre_affaire(cum=False, pay_methode=0):
    today = datetime.date.today()
    currentMonth = datetime.datetime.now().month
    # if cum:
    #     date_ = [datetime.date.today(),datetime.date.today()]
    sale_query = db_session.query(func.coalesce(func.sum(Sales.amount), 0))

    if cum:
        sale_query = sale_query.filter(extract("month", Sales.date) == currentMonth)
    else:
        sale_query = sale_query.filter(Sales.date == today)

    if pay_methode:

        sale_query = sale_query.filter(Sales.paymentmethod_id == pay_methode)

    sum_sales = sale_query.scalar()

    return sum_sales
