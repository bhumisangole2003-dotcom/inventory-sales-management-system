from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite = zero setup, perfect for learning.
DATABASE_URL = "sqlite:///./inventory.db"
# To use PostgreSQL instead, comment the line above and use:
# DATABASE_URL = "postgresql://postgres:password@localhost:5432/inventory_db"

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Gives each request its own database session, then closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
