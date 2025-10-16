# GDK | Scalable Cloud Monitoring System

Production-grade backend system to collect, store, and visualize cloud server metrics with FastAPI, PostgreSQL, Docker, and Grafana.

## Stack
- FastAPI, SQLAlchemy, Alembic
- PostgreSQL
- JWT Auth
- Docker & Docker Compose
- Grafana (provisioned)
- GitHub Actions CI (build + basic checks)

## Highlights
- Built a backend service to monitor metrics (CPU, latency, uptime, memory) with alert thresholds.
- Containerized services with Docker Compose; ready for cloud deployment.
- JWT-secured APIs; metrics stored in PostgreSQL; Grafana dashboards for real-time visualization.
- Health endpoint `/health` and Docker healthchecks for reliability and observability.
- © GDK branding across API, docs, and UI welcome page.

## Quick Start

### 1) Environment
Create a `.env` (optional) to override defaults:
```
POSTGRES_USER=monitor
POSTGRES_PASSWORD=monitorpass
POSTGRES_DB=monitoring
JWT_SECRET_KEY=supersecret
ACCESS_TOKEN_EXPIRE_MINUTES=60
CPU_THRESHOLD=80
LATENCY_THRESHOLD_MS=250
MEMORY_THRESHOLD=85
ADMIN_USERNAME=1287@gmail.com
ADMIN_PASSWORD=1287
GRAFANA_ADMIN_PASSWORD=1287
```

### 2) Run
```
docker compose up -d --build
```
- API: http://localhost:8000 (docs at `/docs`, health at `/health`)
- Grafana: http://localhost:3000 (user: 1287@gmail.com / pass: 1287)
- Postgres: localhost:5432

### 3) Auth
Obtain token:
```
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=1287@gmail.com&password=1287"
```
Use `access_token` with `Authorization: Bearer <token>`.

### 4) Metrics API
- POST /metrics
```
curl -X POST http://localhost:8000/metrics \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"cpu": 72.5, "latency": 130, "uptime": 12345, "memory": 66.2}'
```
- GET /metrics
```
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/metrics?page=1&size=20"
```

### 5) Alerts API
- GET /alerts
```
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/alerts
```

## Migrations
Autogenerate and apply:
```
alembic revision --autogenerate -m "init"
alembic upgrade head
```

## Grafana
A PostgreSQL datasource is provisioned. Import the dashboard at `grafana/dashboards/cloud_metrics.json` if not auto-loaded.

## Development
```
uvicorn app.main:app --reload
```

## Notes
- Tables are created on startup for convenience; use Alembic for production.
- Alerts are stored in the `alerts` table when thresholds are exceeded.
- CI workflow at `.github/workflows/ci.yml` builds on PRs and pushes to `main`.
- © GDK
