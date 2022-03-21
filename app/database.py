from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .settings import Settings


database_url = f"postgresql://{Settings.DB_USERNAME}:{Settings.DB_PASSWORD}" \
               f"@{Settings.DB_HOST}:{Settings.DB_PORT}/{Settings.DB_NAME}"
engine = create_engine(database_url)


def create_connection():
    session = sessionmaker(autocommit=False, bind=engine)
    get_database(session)


def get_database(session):
    database = session()
    try:
        yield database
    finally:
        database.close()
