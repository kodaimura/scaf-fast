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
        encoded = jsonable_encoder(data)
        headers = {}
        if response is not None:
            headers.update(response.headers)

        return JSONResponse(
            content=encoded,
            status_code=status_code,
            headers=headers,
        )

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

    @classmethod
    def error(
        cls,
        data: Any = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> JSONResponse:
        return cls._build_response(
            data=data,
            status_code=status_code,
        )

    @classmethod
    def unauthorized(cls, message: str = "Unauthorized") -> JSONResponse:
        return cls._build_response(
            data={"detail": message},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    @classmethod
    def not_found(cls, message: str = "Resource not found") -> JSONResponse:
        return cls._build_response(
            data={"detail": message},
            status_code=status.HTTP_404_NOT_FOUND,
        )
