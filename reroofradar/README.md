# ReroofRadar

ReroofRadar is a geospatial intelligence platform for roofing contractors. It identifies properties likely to need roof replacement by correlating hail event data with property information.

## Stack

- **Backend**: FastAPI 0.115+, Python 3.11, SQLAlchemy 2.0, GeoAlchemy2
- **Database**: PostgreSQL 16 + PostGIS
- **Cache**: Redis 7
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Maps**: Mapbox GL JS

## Local Setup

```bash
# Copy environment files
cp .env.example .env
cp backend/.env.example backend/.env

# Start all services
docker compose up

# Run database migrations
docker compose exec backend alembic upgrade head

# Seed demo data (optional)
docker compose exec backend python scripts/seed_demo.py
```

The backend will be available at http://localhost:8000 and the frontend at http://localhost:5173.

## API

- `GET /health` - Health check
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user

## Environment Variables

See `.env.example` and `backend/.env.example` for all configurable options.

## Roadmap

- Phase 2: Outreach automation (Twilio, SendGrid, ElevenLabs)
- Phase 3: Morning briefs and scheduling
