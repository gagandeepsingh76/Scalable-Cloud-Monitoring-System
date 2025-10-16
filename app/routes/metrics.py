import os
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..auth.jwt import get_current_user
from ..database import get_db
from ..models import Alert, Metric, User
from ..schemas import MetricCreate, MetricRead, PaginatedMetrics

router = APIRouter()

CPU_THRESHOLD = float(os.getenv("CPU_THRESHOLD", "80"))
LATENCY_THRESHOLD = float(os.getenv("LATENCY_THRESHOLD_MS", "250"))
MEMORY_THRESHOLD = float(os.getenv("MEMORY_THRESHOLD", "85"))


def maybe_trigger_alert(db: Session, metric: Metric) -> None:
	triggered = []
	if metric.cpu is not None and metric.cpu > CPU_THRESHOLD:
		alert = Alert(type="cpu", value=metric.cpu, threshold=CPU_THRESHOLD)
		db.add(alert)
		triggered.append("cpu")
	if metric.latency is not None and metric.latency > LATENCY_THRESHOLD:
		alert = Alert(type="latency", value=metric.latency, threshold=LATENCY_THRESHOLD)
		db.add(alert)
		triggered.append("latency")
	if metric.memory is not None and metric.memory > MEMORY_THRESHOLD:
		alert = Alert(type="memory", value=metric.memory, threshold=MEMORY_THRESHOLD)
		db.add(alert)
		triggered.append("memory")
	if triggered:
		print(f"alerts_triggered={','.join(triggered)} cpu={metric.cpu} latency={metric.latency} memory={metric.memory}")
	# Commit only once by the caller


@router.post("", response_model=MetricRead)
def create_metric(
	payload: MetricCreate,
	db: Session = Depends(get_db),
	user: User = Depends(get_current_user),
):
	metric = Metric(
		cpu=payload.cpu,
		latency=payload.latency,
		uptime=payload.uptime,
		memory=payload.memory,
	)
	db.add(metric)
	maybe_trigger_alert(db, metric)
	db.commit()
	db.refresh(metric)
	return metric


@router.get("", response_model=PaginatedMetrics)
def list_metrics(
	page: int = Query(1, ge=1),
	size: int = Query(20, ge=1, le=200),
	min_cpu: Optional[float] = Query(None, ge=0, le=100),
	max_cpu: Optional[float] = Query(None, ge=0, le=100),
	min_latency: Optional[float] = Query(None, ge=0),
	max_latency: Optional[float] = Query(None, ge=0),
	db: Session = Depends(get_db),
	user: User = Depends(get_current_user),
):
	query = db.query(Metric)
	if min_cpu is not None:
		query = query.filter(Metric.cpu >= min_cpu)
	if max_cpu is not None:
		query = query.filter(Metric.cpu <= max_cpu)
	if min_latency is not None:
		query = query.filter(Metric.latency >= min_latency)
	if max_latency is not None:
		query = query.filter(Metric.latency <= max_latency)

	total = query.with_entities(func.count(Metric.id)).scalar() or 0
	items = (
		query.order_by(Metric.timestamp.desc())
		.offset((page - 1) * size)
		.limit(size)
		.all()
	)
	return PaginatedMetrics(items=items, total=total, page=page, size=size)

