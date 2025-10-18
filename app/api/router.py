from fastapi import APIRouter
from app.api.endpoints import accounts, reports, approvals

api_router = APIRouter()
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
