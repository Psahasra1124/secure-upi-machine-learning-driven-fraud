from fastapi import APIRouter

from app.api.routes import admin, analytics, auth, predictions, transactions

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(predictions.router)
api_router.include_router(transactions.router)
api_router.include_router(analytics.router)
api_router.include_router(admin.router)

