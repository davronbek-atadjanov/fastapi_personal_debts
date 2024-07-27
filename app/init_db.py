from database import Base, engine
from models import Setting, Debt

Base.metadata.create_all(bind=engine)