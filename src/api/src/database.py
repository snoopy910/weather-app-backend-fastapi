from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config import settings

DATABASE_USER = settings.DATABASE_USER
DATABASE_PASSWORD = settings.DATABASE_PASSWORD
DATABASE_NAME = settings.DATABASE_NAME

engine = create_engine("postgresql://"+DATABASE_USER+":"+DATABASE_PASSWORD+"@localhost/"+DATABASE_NAME)

Base = declarative_base()

SessionLocal = sessionmaker(bind=engine)
