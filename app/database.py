from operator import imod
from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


class SQLITE:
    def __init__(self, app=None):

        self.session = scoped_session(sessionmaker(autocommit=False, autoflush=False))
        self.engine = None
        self.Model = declarative_base(bind=self.engine)
        self.app = app

        if app is not None:
            self.init_app(app)

    def create_all(self):
        self.Model.metadata.create_all(bind=self.engine)

    @property
    def metadata(self):
        """The metadata associated with ``db.Model``."""

        return self.Model.metadata

    def init_app(self, app):

        self.engine = create_engine(
            app.config["DATABASE_URI"], connect_args={"check_same_thread": False}
        )
        self.session.configure(bind=self.engine)

        @app.teardown_appcontext
        def shutdown_session(response_or_exc):

            if response_or_exc is None:
                self.session.commit()
            self.session.remove()
            print("!app teardown", self.session)
            return response_or_exc
