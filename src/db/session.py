from contextlib import contextmanager
from sqlmodel import Session, create_engine

from src.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True)


def SessionLocal():
    return Session(engine)


def get_db():
    with Session(engine) as session:
        yield session


@contextmanager
def get_db_context():
    with Session(engine) as session:
        yield session