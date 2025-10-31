from fastapi import APIRouter
from app.handler.account import handler as account_handler

api_router = APIRouter()
api_router.include_router(account_handler.router, prefix="/accounts", tags=["accounts"])
