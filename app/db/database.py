from sqlalchemy.orm import sessionmaker

from app.db import init_db


def create_connection():
    session = sessionmaker(autocommit=False, bind=init_db.engine)
    db = session()
    try:
        yield db
    finally:
        db.close()


def get_database(session):
    return
