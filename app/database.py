from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# PostgreSQL ma'lumotlar bazasiga bog'lanish uchun engine yaratamiz
# asosisy database
SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:12345@localhost/personal_db'
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
# Declarative_base yaratamiz
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()