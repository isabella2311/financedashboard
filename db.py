from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import os

DB_PATH = os.environ.get("FINANCE_DB_PATH", "finance.db")
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    from models import Transaction, Budget, Goal, Debt, Investment, Account
    Base.metadata.create_all(bind=engine)
