from sqlalchemy.orm import sessionmaker

from app.db import init_db


def create_connection():
    """
        Creates a connection to database and returns a Session variable.
    """
    session = sessionmaker(autocommit=False, bind=init_db.engine)
    db = session()
    try:
        yield db
    finally:
        db.close()


async def async_create_connection():
    """
        Creates a connection to database and returns a Session variable.
    """
    session = sessionmaker(autocommit=False, bind=init_db.engine)
    db = session()
    try:
        return db
    except Exception:
        return None


def get_database(session):
    return
