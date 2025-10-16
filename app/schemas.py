from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class Token(BaseModel):
	access_token: str
	token_type: str


class MetricBase(BaseModel):
	cpu: float = Field(..., ge=0, le=100)
	latency: float = Field(..., ge=0)
	uptime: float = Field(..., ge=0)
	memory: Optional[float] = Field(None, ge=0, le=100)
	timestamp: Optional[datetime] = None


class MetricCreate(MetricBase):
	pass


class MetricRead(MetricBase):
	id: int
	timestamp: datetime

	class Config:
		from_attributes = True


class AlertRead(BaseModel):
	id: int
	type: str
	value: float
	threshold: float
	created_at: datetime

	class Config:
		from_attributes = True


class PaginatedMetrics(BaseModel):
	items: List[MetricRead]
	total: int
	page: int
	size: int

