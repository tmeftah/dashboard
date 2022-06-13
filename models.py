from sqlalchemy import Column, Float, Integer, String, ForeignKey, Boolean
from sqlalchemy.types import Date

from sqlalchemy.orm import relationship
from database import Base
import datetime


class DictMixIn:
    id = Column(Integer, primary_key=True, index=True)
    createdAt = Column(Date, default=datetime.datetime.now)
    updatedAt = Column(Date, default=datetime.datetime.now)

    def to_dict(self):
        return {
            column.name: getattr(self, column.name)
            if not isinstance(getattr(self, column.name), (datetime.datetime, datetime.date))
            else getattr(self, column.name).isoformat()
            for column in self.__table__.columns
        }


class User(Base, DictMixIn):
    __tablename__ = "users"

    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def __repr__(self):
        return f"<User {self.name!r}>"


class Companies(Base, DictMixIn):
    __tablename__ = "companies"

    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    customer = Column(Boolean, default=True)
    supplier = Column(Boolean, default=False)
    phone = Column(String(120))

    sales = relationship("Sales", back_populates="company")
    recovers = relationship("Recovers", back_populates="company")
    payments = relationship("Payments", back_populates="company")
    reconciliations = relationship("Reconciliations", back_populates="company")

    def __init__(self, name=None, email=None, customer=True, supplier=False):
        self.name = name
        self.email = email
        self.customer = customer
        self.supplier = supplier

    @property
    def is_customer(self):
        return self.customer

    @property
    def is_supplier(self):
        return self.supplier

    def __repr__(self):
        return f"<User {self.name!r}>"


class Sales(Base, DictMixIn):
    __tablename__ = "sales"

    categorie_id = Column(Integer, ForeignKey("salescategories.id"), nullable=False)
    paymentmethod_id = Column(Integer, ForeignKey("paymentmethod.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    date = Column(Date, default=datetime.datetime.now)

    amount = Column(Float, default=0.0)
    comment = Column(String(50), nullable=False)

    categorie = relationship("SalesCategories", back_populates="sales")
    paymentmethod = relationship("PaymentMethod", back_populates="sales")
    company = relationship("Companies", back_populates="sales")

    def __init__(
        self,
        categorie_id=None,
        company_id=None,
        paymentmethod_id=None,
        date=None,
        amount=0.0,
        comment=None,
    ):

        self.categorie_id = categorie_id
        self.company_id = company_id
        self.paymentmethod_id = paymentmethod_id
        self.date = date
        self.amount = amount
        self.comment = comment

    def __repr__(self):
        return f"<Sales {self.categorie.name!r}>"


class SalesCategories(Base, DictMixIn):
    __tablename__ = "salescategories"

    name = Column(String(50), nullable=False)
    sales = relationship("Sales", back_populates="categorie")

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return f"<Sales {self.name!r}>"


class PaymentMethod(Base, DictMixIn):
    __tablename__ = "paymentmethod"

    name = Column(String(50), nullable=False)
    sales = relationship("Sales", back_populates="paymentmethod")
    costsmappings = relationship("CostsMapping", back_populates="paymentmethod")
    purchasings = relationship("Purchasing", back_populates="paymentmethod")
    recovers = relationship("Recovers", back_populates="paymentmethod")
    payments = relationship("Payments", back_populates="paymentmethod")
    reconciliations = relationship("Reconciliations", back_populates="paymentmethod")

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return f"<Sales {self.name!r}>"


class CostsDef(Base, DictMixIn):
    __tablename__ = "costsdef"

    name = Column(String(50), nullable=False)
    fixed = Column(Boolean, default=False)
    costsmappings = relationship("CostsMapping", back_populates="costsdef")

    def __init__(self, name=None, fixed=False):
        self.name = name
        self.fixed = fixed

    def __repr__(self):
        return f"<CostsDef {self.name!r}>"


class CostsMapping(Base, DictMixIn):
    __tablename__ = "costsmapping"

    cost_id = Column(Integer, ForeignKey("costsdef.id"), nullable=False)
    paymentmethod_id = Column(Integer, ForeignKey("paymentmethod.id"), nullable=False)

    amount = Column(Float, default=0.0)
    date = Column(Date, default=datetime.datetime.now)
    comment = Column(String(50), nullable=False)

    costsdef = relationship("CostsDef", back_populates="costsmappings")
    paymentmethod = relationship("PaymentMethod", back_populates="costsmappings")

    def __init__(
        self,
        cost_id=cost_id,
        paymentmethod_id=paymentmethod_id,
        amount=amount,
        date=date,
        comment=comment,
    ):

        self.cost_id = cost_id
        self.paymentmethod_id = paymentmethod_id
        self.amount = amount
        self.date = date
        self.comment = comment

    def __repr__(self):
        return f"<CostsMapping {self.id!r}>"


class Purchasing(Base, DictMixIn):
    __tablename__ = "purchasing"

    paymentmethod_id = Column(Integer, ForeignKey("paymentmethod.id"), nullable=False)
    comment = Column(String(50), nullable=False)

    amount = Column(Float, default=0.0)
    date = Column(Date, default=datetime.datetime.now)
    month_for = Column(Date, default=datetime.datetime.now)

    paymentmethod = relationship("PaymentMethod", back_populates="purchasings")

    def __init__(
        self,
        paymentmethod_id=paymentmethod_id,
        amount=amount,
        date=date,
        comment=comment,
    ):

        self.paymentmethod_id = paymentmethod_id
        self.amount = amount
        self.date = date
        self.comment = comment

    def __repr__(self):
        return f"<Purchasing {self.id!r}>"


class Recovers(Base, DictMixIn):
    __tablename__ = "recovers"

    # categorie_id = Column(Integer, ForeignKey("salescategories.id"), nullable=False)
    paymentmethod_id = Column(Integer, ForeignKey("paymentmethod.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    date = Column(Date, default=datetime.datetime.now)

    amount = Column(Float, default=0.0)
    comment = Column(String(50), nullable=False)

    # categorie = relationship("SalesCategories", back_populates="sales")
    paymentmethod = relationship("PaymentMethod", back_populates="recovers")
    company = relationship("Companies", back_populates="recovers")

    def __init__(
        self,
        # categorie_id=None,
        company_id=None,
        paymentmethod_id=None,
        date=None,
        amount=0.0,
        comment=None,
    ):

        # self.categorie_id = categorie_id
        self.company_id = company_id
        self.paymentmethod_id = paymentmethod_id
        self.date = date
        self.amount = amount
        self.comment = comment

    def __repr__(self):
        return f"<Recovers {self.company.name!r}>"


class Reconciliations(Base, DictMixIn):
    __tablename__ = "reconciliations"

    # categorie_id = Column(Integer, ForeignKey("salescategories.id"), nullable=False)
    paymentmethod_id = Column(Integer, ForeignKey("paymentmethod.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    cashing = Column(Boolean, default=True)

    date = Column(Date, default=datetime.datetime.now)

    amount = Column(Float, default=0.0)
    comment = Column(String(50), nullable=False)

    # categorie = relationship("SalesCategories", back_populates="sales")
    paymentmethod = relationship("PaymentMethod", back_populates="reconciliations")
    company = relationship("Companies", back_populates="reconciliations")

    def __init__(
        self,
        # categorie_id=None,
        cashing=None,
        company_id=None,
        paymentmethod_id=None,
        date=None,
        amount=0.0,
        comment=None,
    ):

        # self.categorie_id = categorie_id
        self.company_id = company_id
        self.paymentmethod_id = paymentmethod_id
        self.cashing = cashing
        self.date = date
        self.amount = amount
        self.comment = comment

    def __repr__(self):
        return f"<Reconciliations {self.id!r}>"


class Stocks(Base, DictMixIn):
    __tablename__ = "stocks"

    amount = Column(Float, default=0.0)
    date = Column(Date, default=datetime.datetime.now)
    comment = Column(String(50), nullable=False)

    def __init__(
        self,
        amount=0.0,
        date=None,
        comment=None,
    ):

        self.amount = amount
        self.date = date

        self.comment = comment

    def __repr__(self):
        return f"<Stocks {self.id!r}>"


class Payments(Base, DictMixIn):
    __tablename__ = "payments"

    # categorie_id = Column(Integer, ForeignKey("salescategories.id"), nullable=False)
    paymentmethod_id = Column(Integer, ForeignKey("paymentmethod.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    date = Column(Date, default=datetime.datetime.now)

    amount = Column(Float, default=0.0)
    comment = Column(String(50), nullable=False)

    # categorie = relationship("SalesCategories", back_populates="sales")
    paymentmethod = relationship("PaymentMethod", back_populates="payments")
    company = relationship("Companies", back_populates="payments")

    def __init__(
        self,
        # categorie_id=None,
        company_id=None,
        paymentmethod_id=None,
        date=None,
        amount=0.0,
        comment=None,
    ):

        # self.categorie_id = categorie_id
        self.company_id = company_id
        self.paymentmethod_id = paymentmethod_id
        self.date = date
        self.amount = amount
        self.comment = comment

    def __repr__(self):
        return f"<Recovers {self.company.name!r}>"
