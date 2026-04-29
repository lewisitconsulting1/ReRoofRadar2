from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api.auth import router as auth_router
from app.api.campaigns import router as campaigns_router
from app.api.health import router as health_router
from app.core.security import decode_access_token

app = FastAPI(title="ReroofRadar", version="0.1.0")

app.include_router(health_router, prefix="/api")
app.include_router(auth_router)
app.include_router(campaigns_router)


@app.middleware("http")
async def jwt_required_middleware(request: Request, call_next):
    path = request.url.path

    if path in ("/health", "/api/health", "/docs", "/openapi.json", "/redoc"):
        return await call_next(request)

    if path.startswith("/api/auth/"):
        return await call_next(request)

    if not path.startswith("/api/"):
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Not authenticated"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header.split(" ", 1)[1]
    payload = decode_access_token(token)
    if payload is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid or expired token"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await call_next(request)
