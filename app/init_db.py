from app.models import User, Setting, DebtName, Debt
from app.database import Base, engine
Base.metadata.create_all(bind=engine)