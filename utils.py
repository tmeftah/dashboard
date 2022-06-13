from platform import python_branch
from database import db_session
from sqlalchemy.sql import func
from sqlalchemy import extract
from models import Sales, Recovers, CostsMapping, Purchasing, Reconciliations
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


def get_sum_reconciliations(company_id=0, pay_methode_id=0):
    query = db_session.query(func.coalesce(func.sum(Reconciliations.amount), 0)).filter(
        Reconciliations.cashing == True
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

    sum_encaissements = get_sum_reconciliations(company, pay_methode)

    return sum_sales + sum_recovers - sum_encaissements


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
    return 0


def get_engagements(pay_methode=1):
    sum_cost = (
        db_session.query(func.coalesce(func.sum(CostsMapping.amount), 0))
        .filter(CostsMapping.paymentmethod_id == pay_methode)
        .scalar()
    )

    sum_purchasing = (
        db_session.query(func.coalesce(func.sum(Purchasing.amount), 0))
        .filter(Purchasing.paymentmethod_id == pay_methode)
        .scalar()
    )

    return sum_cost + sum_purchasing


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
