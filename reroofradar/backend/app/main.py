from fastapi import FastAPI

from app.api.health import router as health_router

app = FastAPI(title="ReroofRadar", version="0.1.0")

app.include_router(health_router, prefix="/api")
app.include_router(health_router)
