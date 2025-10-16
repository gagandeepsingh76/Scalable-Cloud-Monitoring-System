from datetime import timedelta
import os

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import User
from .schemas import Token
from .auth.jwt import authenticate_user, create_access_token
from .routes.metrics import router as metrics_router
from .routes.alerts import router as alerts_router

app = FastAPI(
	title="GDK | Scalable Cloud Monitoring System",
	version="1.0.0",
	description="© GDK. Collects cloud metrics (CPU, latency, uptime, memory), stores in PostgreSQL, triggers alerts, visualizes via Grafana.",
	contact={"name": "GDK", "email": "support@gdk.example"},
	license_info={"name": "© GDK"},
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Create tables if not present (migrations are recommended for prod)
Base.metadata.create_all(bind=engine)

@app.middleware("http")
async def add_brand_headers(request, call_next):
	response: Response = await call_next(request)
	response.headers["X-Powered-By"] = "GDK"
	response.headers["X-GDK-Copyright"] = "© GDK"
	return response

@app.get("/", tags=["home"], include_in_schema=False)
def home() -> Response:
	return Response(
		content=(
			"""
			<!doctype html>
			<html lang="en"><head><meta charset="utf-8"><title>GDK | Cloud Monitoring</title>
			<style>body{font-family:system-ui,Segoe UI,Roboto,Helvetica,Arial,sans-serif;background:#0b1020;color:#e6e8ef;display:flex;align-items:center;justify-content:center;height:100vh;margin:0} .card{background:#141a2b;border:1px solid #253055;border-radius:12px;padding:28px;max-width:720px;box-shadow:0 10px 30px rgba(0,0,0,.35)} h1{margin:0 0 8px;font-size:28px} p{margin:6px 0 0;color:#a9b1c7} a{color:#7aa2f7;text-decoration:none} a:hover{text-decoration:underline}</style>
			</head><body><div class="card">
			<h1>GDK | Scalable Cloud Monitoring System</h1>
			<p>© GDK. Explore the <a href="/docs">API Docs</a> or <a href="/health">Health</a>.</p>
			</div></body></html>
			"""
		),
		media_type="text/html",
	)

@app.get("/health", tags=["health"]) 
def health() -> dict:
	return {"status": "ok", "brand": "GDK"}

@app.on_event("startup")
def create_admin_if_missing() -> None:
	from passlib.context import CryptContext
	pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

	username = os.getenv("ADMIN_USERNAME", "admin")
	password = os.getenv("ADMIN_PASSWORD", "adminpass")
	with Session(bind=engine) as db:
		user = db.query(User).filter(User.username == username).first()
		if user is None:
			user = User(username=username, password_hash=pwd_context.hash(password), role="admin")
			db.add(user)
			db.commit()

@app.post("/auth/login", response_model=Token, tags=["auth"], summary="Get JWT access token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
	user = authenticate_user(db, form_data.username, form_data.password)
	if not user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
	access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")))
	access_token = create_access_token(data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires)
	return Token(access_token=access_token, token_type="bearer")

app.include_router(metrics_router, prefix="/metrics", tags=["metrics"])
app.include_router(alerts_router, prefix="/alerts", tags=["alerts"])

