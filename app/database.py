from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# PostgreSQL ma'lumotlar bazasiga bog'lanish uchun engine yaratamiz
engine = create_engine('postgresql://postgres:12345@localhost/personal_db', echo=True)

# Declarative_base yaratamiz
Base = declarative_base()
session = sessionmaker()
session = session(bind=engine)