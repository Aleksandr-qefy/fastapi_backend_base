from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import config as c

SQLALCHEMY_DATABASE_URL = f"postgresql://{c.DB_USER}:{c.DB_PASSWORD}@{c.DB_SERVER}/{c.DB_NAME}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
