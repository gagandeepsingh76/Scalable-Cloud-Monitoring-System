from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..auth.jwt import get_current_user
from ..database import get_db
from ..models import Alert, User
from ..schemas import AlertRead

router = APIRouter()


@router.get("", response_model=list[AlertRead])
def list_alerts(
	page: int = Query(1, ge=1),
	size: int = Query(50, ge=1, le=200),
	db: Session = Depends(get_db),
	user: User = Depends(get_current_user),
):
	query = db.query(Alert).order_by(Alert.created_at.desc())
	items = query.offset((page - 1) * size).limit(size).all()
	return items

