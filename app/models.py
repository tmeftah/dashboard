import datetime

from flask import session, abort
from flask_login import AnonymousUserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Float, Integer, String, ForeignKey, Boolean, CheckConstraint
from sqlalchemy.types import Date
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func


from . import db, login_manager


class DictMixIn:
    id = Column(Integer, primary_key=True, index=True)
    createdAt = Column(Date, default=datetime.datetime.now)
    updatedAt = Column(Date, default=datetime.datetime.now)

    @classmethod
    def query(cls):
        if session.get("tenant") in [tenant.id for tenant in current_user.tenants]:
            return db.session.query(cls).filter_by(tenant_id=session.get("tenant"))
        abort(403)

    @classmethod
    def query_sum(cls):
        if session.get("tenant") in [tenant.id for tenant in current_user.tenants]:
            return db.session.query(func.coalesce(func.sum(cls.amount), 0)).filter_by(
                tenant_id=session.get("tenant")
            )
        abort(403)

    def to_dict(self):
        return {
            column.name: getattr(self, column.name)
            if not isinstance(getattr(self, column.name), (datetime.datetime, datetime.date))
            else getattr(self, column.name).isoformat()
            for column in self.__table__.columns
        }


class TenantMix:
    @declared_attr
    def tenant_id(cls):
        return Column(Integer, ForeignKey("tenants.id"), nullable=False)


class UserMix:
    @declared_attr
    def user_id(cls):
        return Column(Integer, ForeignKey("users.id"), nullable=False)


# -------------------------------  Role Based Authorization   ----------------------------------


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class Role(db.Model, DictMixIn):
    __tablename__ = "roles"

    name = Column(String(64), unique=True)
    default = Column(Boolean, default=False, index=True)
    permissions = Column(Integer)
    users = relationship("User", backref="role", lazy="dynamic")

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def init_data():

        roles = {
            "User": [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            "Moderator": [
                Permission.FOLLOW,
                Permission.COMMENT,
                Permission.WRITE,
                Permission.MODERATE,
            ],
            "Administrator": [
                Permission.FOLLOW,
                Permission.COMMENT,
                Permission.WRITE,
                Permission.MODERATE,
                Permission.ADMIN,
            ],
        }
        default_role = "User"
        for r in roles:
            role = db.session.query(Role).filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = role.name == default_role
            db.session.add(role)

        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return "<Role %r>" % self.name


class Tenants(db.Model, DictMixIn):
    __tablename__ = "tenants"

    name = Column(String(50), unique=True)
    email = Column(String(120), nullable=False, unique=True)  # TODO: unique=True,
    phone = Column(String(120))
    users = relationship("TenantUsers", back_populates="tenant")

    companies = relationship("Companies", backref="tenant", lazy="dynamic")

    def __init__(self, **kwargs):
        super(Tenants, self).__init__(**kwargs)

    @classmethod
    def init_data(cls):
        holding = cls(
            name="Hodling",
            email="Hodling@Hodling.com",
        )

        db.session.add(holding)
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            print(e)
            db.session.rollback()

    def __repr__(self):
        return f"<Tenant {self.name!r}>"


class User(db.Model, DictMixIn):
    __tablename__ = "users"

    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    password_hash = Column(String(100))
    role_id = Column(Integer, ForeignKey("roles.id"))
    authenticated = Column(Boolean, default=False)

    tenants = relationship("TenantUsers", back_populates="user")

    def __init__(self, name=None, email=None, password=None, role=None, tenant=None):
        self.name = name
        self.email = email
        self.password = password
        self.role = role

        if self.role is None:
            self.role = db.session.query(Role).filter_by(default=True).first()

    @classmethod
    def init_data(cls):
        admin = cls(
            name="Saleh",
            email="user1@test.com",
            password="test",
        )
        admin.role = db.session.query(Role).filter_by(name="Administrator").first()

        tenant = db.session.query(Tenants).first()
        tenantuser = TenantUsers()
        tenantuser.user = admin
        tenantuser.tenant = tenant
        db.session.add(admin)
        db.session.add(tenantuser)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            print(e)
            db.session.rollback()

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

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

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def __repr__(self):
        return f"<User {self.name!r}>"


class TenantUsers(db.Model, DictMixIn):
    __tablename__ = "tenant_users"

    def __init__(self, **kwargs):
        super(TenantUsers, self).__init__(**kwargs)

    tenant_id = Column(ForeignKey("tenants.id"))
    user_id = Column(ForeignKey("users.id"))

    tenant = relationship("Tenants", back_populates="users")
    user = relationship("User", back_populates="tenants")

    def __repr__(self):
        return f"<TenantUsers {self.tenant.name!r},{self.user.name!r}>"


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    user = db.session.query(User).get(int(user_id))
    return user


class Companies(db.Model, DictMixIn, TenantMix):
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
        self.tenant_id = int(session["tenant"])
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


class Sales(db.Model, DictMixIn, TenantMix):
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

        self.tenant_id = int(session["tenant"])
        # self.categorie_id = categorie_id
        self.company_id = company_id
        self.paymentmethod_id = paymentmethod_id
        self.date = date
        self.amount = amount
        self.comment = comment
        self.document_number = document_number

    def __repr__(self):
        return f"<Sales {self.categorie.name!r}>"


class SalesCategories(db.Model, DictMixIn, TenantMix):
    __tablename__ = "salescategories"

    name = Column(String(50), nullable=False)
    # sales = relationship("Sales", back_populates="categorie")

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return f"<Sales {self.name!r}>"


class PaymentMethod(db.Model, DictMixIn):
    __tablename__ = "paymentmethod"

    name = Column(String(50), nullable=False, unique=True)
    sales = relationship("Sales", back_populates="paymentmethod")
    costsmappings = relationship("CostsMapping", back_populates="paymentmethod")
    purchasings = relationship("Purchasing", back_populates="paymentmethod")
    recovers = relationship("Recovers", back_populates="paymentmethod")
    payments = relationship("Payments", back_populates="paymentmethod")
    reconciliations = relationship("Reconciliations", back_populates="paymentmethod")

    def __init__(self, name=None):
        self.name = name

    @classmethod
    def init_data(cls):

        db.session.add(cls(name="Espèce"))  # 1
        db.session.add(cls(name="Chèque"))  # 2
        db.session.add(cls(name="Traite"))  # 3
        db.session.add(cls(name="Credit"))  # 4
        db.session.add(cls(name="TPE"))  # 5
        db.session.add(cls(name="Ticket Resto"))  # 6
        db.session.add(cls(name="Virement Banquaire"))  # 7

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            print(e)
            db.session.rollback()

    def __repr__(self):
        return f"<Sales {self.name!r}>"


class CostsDef(db.Model, DictMixIn, TenantMix):
    __tablename__ = "costsdef"

    name = Column(String(50), nullable=False)
    fixed = Column(Boolean, default=False)
    costsmappings = relationship("CostsMapping", back_populates="costsdef")
    payments = relationship("Payments", back_populates="costsdef")

    reconciliations = relationship("Reconciliations", back_populates="cost")

    def __init__(self, name=None, fixed=False):
        self.tenant_id = int(session["tenant"])
        self.name = name
        self.fixed = fixed

    def __repr__(self):
        return f"<CostsDef {self.name!r}>"


class CostsMapping(db.Model, DictMixIn, TenantMix):
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
        self.tenant_id = int(session["tenant"])
        self.cost_id = cost_id
        self.paymentmethod_id = paymentmethod_id
        self.amount = amount
        self.date = date
        self.comment = comment
        self.document_number = document_number

    def __repr__(self):
        return f"<CostsMapping {self.id!r}>"


class Purchasing(db.Model, DictMixIn, TenantMix):
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

        self.tenant_id = int(session["tenant"])
        self.paymentmethod_id = paymentmethod_id
        self.company_id = company_id
        self.amount = amount
        self.date = date
        self.comment = comment
        self.document_number = document_number

    def __repr__(self):
        return f"<Purchasing {self.id!r}>"


class Recovers(db.Model, DictMixIn, TenantMix):
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

        self.tenant_id = int(session["tenant"])
        # self.categorie_id = categorie_id
        self.company_id = company_id
        self.paymentmethod_id = paymentmethod_id
        self.date = date
        self.amount = amount
        self.comment = comment
        self.document_number = document_number

    def __repr__(self):
        return f"<Recovers {self.company.name!r}>"


class Reconciliations(db.Model, DictMixIn, TenantMix):
    __tablename__ = "reconciliations"

    # categorie_id = Column(Integer, ForeignKey("salescategories.id"), nullable=False)
    paymentmethod_id = Column(Integer, ForeignKey("paymentmethod.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"))
    cost_id = Column(Integer, ForeignKey("costsdef.id"))

    cashing = Column(Boolean, default=True)

    date = Column(Date, default=datetime.datetime.now)

    amount = Column(Float, default=0.0)
    comment = Column(String(50), nullable=False)

    # categorie = relationship("SalesCategories", back_populates="sales")
    paymentmethod = relationship("PaymentMethod", back_populates="reconciliations")
    company = relationship("Companies", back_populates="reconciliations")
    cost = relationship("CostsDef", back_populates="reconciliations")

    # table level CHECK constraint.  'name' is optional.

    __table_args__ = (
        CheckConstraint(
            "(company_id  is null or cost_id is null) and not (company_id is null and cost_id is null)",
            name="only_one_value",
        ),
    )

    def __init__(
        self,
        cost_id=None,
        cashing=None,
        company_id=None,
        paymentmethod_id=None,
        date=None,
        amount=0.0,
        comment=None,
    ):

        self.tenant_id = int(session["tenant"])
        self.cost_id = cost_id
        self.company_id = company_id
        self.paymentmethod_id = paymentmethod_id
        self.cashing = cashing
        self.date = date
        self.amount = amount
        self.comment = comment

    def __repr__(self):
        return f"<Reconciliations {self.id!r}>"


class Stocks(db.Model, DictMixIn, TenantMix):
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

        self.tenant_id = int(session["tenant"])
        self.amount = amount
        self.date = date

        self.comment = comment

    def __repr__(self):
        return f"<Stocks {self.id!r}>"


class Payments(db.Model, DictMixIn, TenantMix):
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

        self.tenant_id = int(session["tenant"])
        # self.categorie_id = categorie_id
        self.company_id = company_id
        self.cost_id = cost_id
        self.paymentmethod_id = paymentmethod_id
        self.date = date
        self.amount = amount
        self.comment = comment
        self.document_number = document_number

    def __repr__(self):
        return f"<Payments {self.id}>"
