from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class User(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
	password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
	role: Mapped[str] = mapped_column(String(50), default="user", nullable=False)


class Metric(Base):
	__tablename__ = "metrics"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	cpu: Mapped[float] = mapped_column(Float, nullable=False)
	latency: Mapped[float] = mapped_column(Float, nullable=False)
	uptime: Mapped[float] = mapped_column(Float, nullable=False)
	memory: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
	timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True, nullable=False)


class Alert(Base):
	__tablename__ = "alerts"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., cpu, latency, memory
	value: Mapped[float] = mapped_column(Float, nullable=False)
	threshold: Mapped[float] = mapped_column(Float, nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True, nullable=False)

