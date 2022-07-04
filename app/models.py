from sqlalchemy import Column, Float, Integer, String, ForeignKey, Boolean, CheckConstraint
from sqlalchemy.types import Date

from sqlalchemy.orm import relationship

import datetime

from . import Base, db_session, login_manager


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
    password = Column(String(100))
    authenticated = Column(Boolean, default=False)

    def __init__(self, name=None, email=None, password=None):
        self.name = name
        self.email = email
        self.password = password

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        # False as we do not support annonymity
        return False

    def get_id(self):
        # returns the user e-mail
        return self.id

    def __repr__(self):
        return f"<User {self.name!r}>"


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    user = db_session.query(User).get(int(user_id))
    return user


class Companies(Base, DictMixIn):
    __tablename__ = "companies"

    name = Column(String(50), unique=True)
    email = Column(String(120), nullable=True)  # TODO: unique=True,
    customer = Column(Boolean, default=True)
    supplier = Column(Boolean, default=False)
    phone = Column(String(120))

    sales = relationship("Sales", back_populates="company")
    purchasings = relationship("Purchasing", back_populates="company")
    recovers = relationship("Recovers", back_populates="company")
    payments = relationship("Payments", back_populates="company")
    reconciliations = relationship("Reconciliations", back_populates="company")

    def __init__(self, name=None, email=None, phone=None, customer=True, supplier=False):
        self.name = name
        self.email = email
        self.customer = customer
        self.supplier = supplier
        self.phone = phone

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

    # categorie_id = Column(Integer, ForeignKey("salescategories.id"), nullable=False)
    paymentmethod_id = Column(Integer, ForeignKey("paymentmethod.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    date = Column(Date, default=datetime.datetime.now())

    document_number = Column(String(50))
    due_date = Column(Date, default=datetime.datetime.now())

    amount = Column(Float, default=0.0)
    comment = Column(String(50), nullable=False)

    document_filename = Column(String(50))

    # categorie = relationship("SalesCategories", back_populates="sales")
    paymentmethod = relationship("PaymentMethod", back_populates="sales")
    company = relationship("Companies", back_populates="sales")

    def __init__(
        self,
        # categorie_id=None,
        company_id=None,
        paymentmethod_id=None,
        date=None,
        amount=0.0,
        comment=None,
        document_number="nop",
    ):

        # self.categorie_id = categorie_id
        self.company_id = company_id
        self.paymentmethod_id = paymentmethod_id
        self.date = date
        self.amount = amount
        self.comment = comment
        self.document_number = document_number

    def __repr__(self):
        return f"<Sales {self.categorie.name!r}>"


class SalesCategories(Base, DictMixIn):
    __tablename__ = "salescategories"

    name = Column(String(50), nullable=False)
    # sales = relationship("Sales", back_populates="categorie")

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
    payments = relationship("Payments", back_populates="costsdef")

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

    document_number = Column(String(50), nullable=False)
    due_date = Column(Date, default=datetime.datetime.now)
    document_filename = Column(String(50))

    costsdef = relationship("CostsDef", back_populates="costsmappings")
    paymentmethod = relationship("PaymentMethod", back_populates="costsmappings")

    def __init__(
        self,
        cost_id=cost_id,
        paymentmethod_id=paymentmethod_id,
        amount=amount,
        date=date,
        comment=comment,
        document_number="nop",
    ):

        self.cost_id = cost_id
        self.paymentmethod_id = paymentmethod_id
        self.amount = amount
        self.date = date
        self.comment = comment
        self.document_number = document_number

    def __repr__(self):
        return f"<CostsMapping {self.id!r}>"


class Purchasing(Base, DictMixIn):
    __tablename__ = "purchasing"

    paymentmethod_id = Column(Integer, ForeignKey("paymentmethod.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    comment = Column(String(50), nullable=False)

    amount = Column(Float, default=0.0)
    date = Column(Date, default=datetime.datetime.now)
    month_for = Column(Date, default=datetime.datetime.now)

    document_number = Column(String(50), nullable=False)
    due_date = Column(Date, default=datetime.datetime.now)
    document_filename = Column(String(50))

    paymentmethod = relationship("PaymentMethod", back_populates="purchasings")
    company = relationship("Companies", back_populates="purchasings")

    def __init__(
        self,
        paymentmethod_id=paymentmethod_id,
        company_id=company_id,
        amount=amount,
        date=date,
        comment=comment,
        document_number="nop",
    ):

        self.paymentmethod_id = paymentmethod_id
        self.company_id = company_id
        self.amount = amount
        self.date = date
        self.comment = comment
        self.document_number = document_number

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

    document_number = Column(String(50), nullable=False)
    due_date = Column(Date, default=datetime.datetime.now)
    document_filename = Column(String(50))

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
        document_number="nop",
    ):

        # self.categorie_id = categorie_id
        self.company_id = company_id
        self.paymentmethod_id = paymentmethod_id
        self.date = date
        self.amount = amount
        self.comment = comment
        self.document_number = document_number

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
    company_id = Column(Integer, ForeignKey("companies.id"))
    cost_id = Column(Integer, ForeignKey("costsdef.id"))
    date = Column(Date, default=datetime.datetime.now)

    amount = Column(Float, default=0.0)
    comment = Column(String(50), nullable=False)

    document_number = Column(String(50), nullable=False)
    due_date = Column(Date, default=datetime.datetime.now)
    document_filename = Column(String(50))

    # categorie = relationship("SalesCategories", back_populates="sales")
    paymentmethod = relationship("PaymentMethod", back_populates="payments")
    company = relationship("Companies", back_populates="payments")
    costsdef = relationship("CostsDef", back_populates="payments")

    # table level CHECK constraint.  'name' is optional.

    __table_args__ = (
        CheckConstraint(
            "(company_id  is null or cost_id is null) and not (company_id is null and cost_id is null)",
            name="only_one_value",
        ),
    )

    def __init__(
        self,
        # categorie_id=None,
        company_id=None,
        cost_id=None,
        paymentmethod_id=None,
        date=None,
        amount=0.0,
        comment=None,
        document_number="nop",
    ):

        # self.categorie_id = categorie_id
        self.company_id = company_id
        self.cost_id = cost_id
        self.paymentmethod_id = paymentmethod_id
        self.date = date
        self.amount = amount
        self.comment = comment
        self.document_number = document_number

    def __repr__(self):
        return f"<Recovers {self.company.name!r}>"