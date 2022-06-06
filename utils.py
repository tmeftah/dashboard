from database import db_session
from sqlalchemy.sql import func
from models import Sales, Recovers, CostsMapping, Purchasing, Rapprochements


def get_sold_client():
    sum_credits = (
        db_session.query(func.coalesce(func.sum(Sales.amount), 0))
        .filter(Sales.paymentmethod_id == 4)
        .scalar()
    )
    sum_rapprochements = db_session.query(func.coalesce(func.sum(Recovers.amount), 0)).scalar()

    return sum_credits - sum_rapprochements


def get_sold_portefeuille(pay_methode=1):
    # le raprochement doit etre pris en compte
    sum_sales = (
        db_session.query(func.coalesce(func.sum(Sales.amount), 0))
        .filter(Sales.paymentmethod_id == pay_methode)
        .scalar()
    )

    sum_rapprochements = (
        db_session.query(func.coalesce(func.sum(Recovers.amount), 0))
        .filter(Recovers.paymentmethod_id == pay_methode)
        .scalar()
    )

    sum_encaissements = (
        db_session.query(func.coalesce(func.sum(Rapprochements.amount), 0))
        .filter(Rapprochements.cashing == True, Rapprochements.paymentmethod_id == pay_methode)
        .scalar()
    )

    return sum_sales + sum_rapprochements - sum_encaissements


def get_impayees(pay_methode=1):
    return 0


def get_banque():
    sum_encaissements = (
        db_session.query(func.coalesce(func.sum(Rapprochements.amount), 0))
        .filter(Rapprochements.cashing == True)
        .scalar()
    )
    sum_decaissements = (
        db_session.query(func.coalesce(func.sum(Rapprochements.amount), 0))
        .filter(Rapprochements.cashing == False)
        .scalar()
    )
    return sum_encaissements - sum_decaissements


def get_caisse():

    sum_sales = (
        db_session.query(func.coalesce(func.sum(Sales.amount), 0))
        .filter(Sales.paymentmethod_id == 1)
        .scalar()
    )

    sum_rapprochements = (
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
        db_session.query(func.coalesce(func.sum(Rapprochements.amount), 0))
        .filter(Rapprochements.cashing == False)
        .scalar()
    )

    return sum_sales + sum_rapprochements - sum_cost - sum_purchasing


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
