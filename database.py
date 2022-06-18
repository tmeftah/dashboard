from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///test.db")
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from models import PaymentMethod, SalesCategories, Companies, CostsDef, User

    # Recreate database each time for demo
    Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)

    # init User
    from werkzeug.security import generate_password_hash

    db_session.add(
        User(
            name="Saleh",
            email="user1@test.com",
            password=generate_password_hash("test"),
        )
    )

    # init clients
    db_session.add(
        Companies(name="Client n°1", email="client1@client.com", customer=True, supplier=False)
    )
    db_session.add(
        Companies(name="Client n°2", email="client2@client.com", customer=True, supplier=False)
    )
    db_session.add(
        Companies(
            name="Fournisseur n°1", email="fournisseur1@client.com", customer=False, supplier=True
        )
    )
    db_session.add(
        Companies(
            name="Fournisseur n°2", email="fournisseur2@client.com", customer=False, supplier=True
        )
    )

    db_session.add(
        Companies(
            name="Client/Fournisseur n°2",
            email="client/fournisseur@client.com",
            customer=True,
            supplier=True,
        )
    )

    # init mode de payment
    db_session.add(PaymentMethod(name="Espèce"))  # 1
    db_session.add(PaymentMethod(name="Chèque"))  # 2
    db_session.add(PaymentMethod(name="Traite"))  # 3
    db_session.add(PaymentMethod(name="Credit"))  # 4
    db_session.add(PaymentMethod(name="TPE"))  # 5
    db_session.add(PaymentMethod(name="Ticket Resto"))  # 6
    db_session.add(PaymentMethod(name="Virement Banquaire"))  # 7

    # init CA categorie
    db_session.add(SalesCategories(name="Gros"))
    db_session.add(SalesCategories(name="Magasin"))

    # init CostDef
    db_session.add(CostsDef(name="LOYER", fixed=True))
    db_session.add(CostsDef(name="Carburant", fixed=False))

    db_session.commit()
