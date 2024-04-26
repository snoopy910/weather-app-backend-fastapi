from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("postgresql://postgres:123@localhost/fastapi_test", echo=True)

Base = declarative_base()

SessionLocal = sessionmaker(bind=engine)
