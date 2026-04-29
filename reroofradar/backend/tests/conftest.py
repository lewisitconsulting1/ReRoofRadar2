import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.orm import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    from fastapi.testclient import TestClient
    from fastapi import FastAPI, Request, status
    from fastapi.responses import JSONResponse
    from app.api.auth import router as auth_router
    from app.api.campaigns import router as campaigns_router
    from app.api.health import router as health_router
    from app.core.security import decode_access_token, create_access_token
    import app.deps as deps_module
    import app.api.auth as auth_module

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    test_app = FastAPI(title="ReroofRadar-Test", version="0.1.0")

    test_app.include_router(health_router, prefix="/api")
    test_app.include_router(auth_router)
    test_app.include_router(campaigns_router)

    test_app.dependency_overrides[deps_module.get_db] = override_get_db

    @test_app.middleware("http")
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

    with TestClient(test_app) as test_client:
        yield test_client

    test_app.dependency_overrides.clear()
