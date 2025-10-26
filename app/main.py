from fastapi import FastAPI, Request, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from app.core.response import ApiResponse
from app.core.logger import logger
from app.api.router import api_router


app = FastAPI(title="scaf-fast", version="1.0.0")
app.include_router(api_router, prefix="/api")


# ===========================
# Exception Handlers
# ===========================


@app.exception_handler(HTTPException)
async def handle_http_exception(request: Request, exc: HTTPException):
    """FastAPI標準のHTTP例外"""
    logger.warning(f"[HTTP {exc.status_code}] {exc.detail} - {request.url}")
    return ApiResponse.error(
        message=exc.detail or "HTTP error",
        data={"status_code": exc.status_code},
    ).to_fastapi_response(status_code=exc.status_code)


@app.exception_handler(SQLAlchemyError)
async def handle_db_error(request: Request, exc: SQLAlchemyError):
    """DB例外"""
    logger.error(f"[DB ERROR] {str(exc)} - {request.url}")
    return ApiResponse.error(
        message="Database error occurred",
        data={"detail": str(exc)},
    ).to_fastapi_response(status_code=500)


@app.exception_handler(ValidationError)
async def handle_validation_error(request: Request, exc: ValidationError):
    """バリデーション例外"""
    logger.info(f"[VALIDATION] {exc.errors()} - {request.url}")
    return ApiResponse.error(
        message="Validation error",
        data={"errors": exc.errors()},
    ).to_fastapi_response(status_code=422)


@app.exception_handler(Exception)
async def handle_generic_error(request: Request, exc: Exception):
    """予期しない例外"""
    logger.exception(f"[UNEXPECTED] {type(exc).__name__}: {exc} - {request.url}")
    return ApiResponse.error(
        message="Internal server error",
        data={"detail": str(exc)},
    ).to_fastapi_response(status_code=500)
