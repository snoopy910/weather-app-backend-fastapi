from src.database import Base, engine
from src.models import Location

print("Creating database ....")

Base.metadata.create_all(engine)
