from typing import Any, Optional
from fastapi import Response, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder  # ← 追加
from pydantic import BaseModel


class ApiResponse(BaseModel):
    """アプリ全体で統一的に利用するAPIレスポンスモデル"""

    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None

    @classmethod
    def _build_response(
        cls,
        success: bool,
        message: Optional[str],
        data: Any,
        status_code: int,
        response: Optional[Response] = None,
    ) -> JSONResponse:
        """共通レスポンス生成ロジック（ヘッダー/クッキー対応）"""
        # Pydanticモデルを辞書化
        payload = cls(success=success, message=message, data=data).model_dump()

        # ✅ datetime や ORM モデルなどを安全にエンコード
        encoded_payload = jsonable_encoder(payload)

        # ResponseヘッダーやCookieの維持
        headers = getattr(response, "headers", None) if response else None

        return JSONResponse(
            content=encoded_payload,
            status_code=status_code,
            headers=headers,
        )

    # ---- 正常系 ---- #
    @classmethod
    def ok(
        cls,
        data: Any = None,
        message: Optional[str] = "OK",
        response: Optional[Response] = None,
        status_code: int = status.HTTP_200_OK,
    ) -> JSONResponse:
        """200 OK"""
        return cls._build_response(
            success=True,
            message=message,
            data=data,
            status_code=status_code,
            response=response,
        )

    @classmethod
    def created(
        cls,
        data: Any = None,
        message: Optional[str] = "Created successfully",
        response: Optional[Response] = None,
    ) -> JSONResponse:
        """201 Created"""
        return cls._build_response(
            success=True,
            message=message,
            data=data,
            status_code=status.HTTP_201_CREATED,
            response=response,
        )

    # ---- エラー系 ---- #
    @classmethod
    def error(
        cls,
        message: str,
        data: Any = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> JSONResponse:
        """400 Bad Request"""
        return cls._build_response(
            success=False,
            message=message,
            data=data,
            status_code=status_code,
        )

    @classmethod
    def unauthorized(cls, message: str = "Unauthorized") -> JSONResponse:
        """401 Unauthorized"""
        return cls._build_response(
            success=False,
            message=message,
            data=None,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    @classmethod
    def not_found(cls, message: str = "Resource not found") -> JSONResponse:
        """404 Not Found"""
        return cls._build_response(
            success=False,
            message=message,
            data=None,
            status_code=status.HTTP_404_NOT_FOUND,
        )
