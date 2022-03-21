from sqlalchemy.orm import sessionmaker

from app.db import init_db


def create_connection():
    session = sessionmaker(autocommit=False, bind=init_db.engine)
    get_database(session())


def get_database(session):
    try:
        yield session()
    finally:
        session.close()
