from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.db.init_db import init_db
from app.services.ml_service import predictor


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Secure UPI Fraud Detection API",
    description=(
        "JWT-protected UPI transaction scoring, transaction history, analytics, "
        "CSV reports, and explainable machine-learning predictions."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["System"])
def health() -> dict:
    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.environment,
        "model_loaded": predictor.is_trained,
        "model_version": predictor.model_version,
    }

