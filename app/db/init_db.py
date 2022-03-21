from app.settings import Settings
from sqlalchemy import create_engine

database_url = f"postgresql://{Settings.DB_USERNAME}:{Settings.DB_PASSWORD}" \
               f"@{Settings.DB_HOST}:{Settings.DB_PORT}/{Settings.DB_NAME}"
engine = create_engine(database_url)
