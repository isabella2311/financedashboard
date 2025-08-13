from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.orm import Mapped, mapped_column
from db import Base
import datetime as dt

class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    date: Mapped[dt.date] = mapped_column(Date, index=True)
    type: Mapped[str] = mapped_column(String(10))  # income | expense
    category: Mapped[str] = mapped_column(String(50))
    account: Mapped[str] = mapped_column(String(50), default="Principal")
    amount: Mapped[float] = mapped_column(Float)
    description: Mapped[str] = mapped_column(String(255), default="")
    tags: Mapped[str] = mapped_column(String(255), default="")

class Budget(Base):
    __tablename__ = "budgets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category: Mapped[str] = mapped_column(String(50))
    month: Mapped[int] = mapped_column(Integer)  # 1-12
    year: Mapped[int] = mapped_column(Integer)
    amount: Mapped[float] = mapped_column(Float)

class Goal(Base):
    __tablename__ = "goals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    target_amount: Mapped[float] = mapped_column(Float)
    current_amount: Mapped[float] = mapped_column(Float, default=0.0)
    deadline: Mapped[dt.date] = mapped_column(Date, nullable=True)

class Debt(Base):
    __tablename__ = "debts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    principal: Mapped[float] = mapped_column(Float)
    rate_apy: Mapped[float] = mapped_column(Float)  # % anual efectiva
    min_payment: Mapped[float] = mapped_column(Float)
    due_day: Mapped[int] = mapped_column(Integer)  # día de mes

class Investment(Base):
    __tablename__ = "investments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    asset: Mapped[str] = mapped_column(String(100))
    broker: Mapped[str] = mapped_column(String(100), default="")
    invested: Mapped[float] = mapped_column(Float)
    current_value: Mapped[float] = mapped_column(Float)
    updated_at: Mapped[dt.date] = mapped_column(Date, default=dt.date.today)

class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(50), default="checking")  # checking, savings, credit
