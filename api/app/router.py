from fastapi import APIRouter, Depends

from app.core.jwt import get_account_id
from app.handler.accounts import router as accounts_router
from app.handler.auth import router as auth_router


api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(accounts_router, dependencies=[Depends(get_account_id)])
