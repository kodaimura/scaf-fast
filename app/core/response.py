from typing import Any, Optional
from fastapi import Response, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


class ApiResponse:
    @staticmethod
    def _build_response(
        data: Any,
        status_code: int,
        response: Optional[Response] = None,
    ) -> JSONResponse:
        if hasattr(data, "model_dump"):
            data = data.model_dump()

        encoded = jsonable_encoder(data)
        headers = dict(response.headers) if response else {}

        return JSONResponse(
            content=encoded,
            status_code=status_code,
            headers=headers,
        )

    # ----------------------------------------
    # 200 OK
    # ----------------------------------------
    @classmethod
    def ok(
        cls,
        data: Any = None,
        response: Optional[Response] = None,
        status_code: int = status.HTTP_200_OK,
    ) -> JSONResponse:
        return cls._build_response(
            data=data,
            status_code=status_code,
            response=response,
        )

    # ----------------------------------------
    # 201 Created
    # ----------------------------------------
    @classmethod
    def created(
        cls,
        data: Any = None,
        response: Optional[Response] = None,
    ) -> JSONResponse:
        return cls._build_response(
            data=data,
            status_code=status.HTTP_201_CREATED,
            response=response,
        )

    # ----------------------------------------
    # 400 Bad Request
    # ----------------------------------------
    @classmethod
    def error(
        cls,
        message: str = "Bad Request",
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> JSONResponse:
        return cls._build_response(
            data={"detail": message},
            status_code=status_code,
        )

    # ----------------------------------------
    # 401 Unauthorized
    # ----------------------------------------
    @classmethod
    def unauthorized(cls, message: str = "Unauthorized") -> JSONResponse:
        return cls._build_response(
            data={"detail": message},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    # ----------------------------------------
    # 404 Not Found
    # ----------------------------------------
    @classmethod
    def not_found(cls, message: str = "Resource not found") -> JSONResponse:
        return cls._build_response(
            data={"detail": message},
            status_code=status.HTTP_404_NOT_FOUND,
        )
