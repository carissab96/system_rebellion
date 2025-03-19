from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import event

#sqlite for development
DATABASE_URL = "SQLITE:///./system_rebellion.db" # or PostgreSql in production

#For PostgreSQL
#DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/system_revellion"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} #only for sqlite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

