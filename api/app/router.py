from fastapi import APIRouter, Depends

from app.core.jwt import get_account_id
from app.handler.auth import router as auth_router
from app.handler.accounts import router as accounts_router

public_router = APIRouter()
protected_router = APIRouter(dependencies=[Depends(get_account_id)])

public_router.include_router(auth_router)
protected_router.include_router(accounts_router)

api_router = APIRouter()
api_router.include_router(public_router)
api_router.include_router(protected_router)
