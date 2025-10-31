from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from app.core.config import config
from app.core.response import ApiResponse
from app.core.logger import logger
from .router import api_router


app = FastAPI(title="scaf-fast", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


# ===========================
# Exception Handlers
# ===========================


@app.exception_handler(HTTPException)
async def handle_http_exception(request: Request, exc: HTTPException):
    logger.warning(f"[HTTP {exc.status_code}] {exc.detail} - {request.url}")
    return ApiResponse.error(
        data={"message": exc.detail or "HTTP error"},
        status_code=exc.status_code,
    )


@app.exception_handler(SQLAlchemyError)
async def handle_db_error(request: Request, exc: SQLAlchemyError):
    logger.error(f"[DB ERROR] {str(exc)} - {request.url}")
    return ApiResponse.error(
        data={"message": "Database error occurred", "detail": str(exc)},
        status_code=500,
    )


@app.exception_handler(ValidationError)
async def handle_validation_error(request: Request, exc: ValidationError):
    logger.info(f"[VALIDATION] {exc.errors()} - {request.url}")
    return ApiResponse.error(
        data={"message": "Validation error", "errors": exc.errors()},
        status_code=422,
    )


@app.exception_handler(Exception)
async def handle_generic_error(request: Request, exc: Exception):
    logger.exception(f"[UNEXPECTED] {type(exc).__name__}: {exc} - {request.url}")
    return ApiResponse.error(
        data={"message": "Internal server error", "detail": str(exc)},
        status_code=500,
    )
