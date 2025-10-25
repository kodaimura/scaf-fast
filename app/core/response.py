from typing import Any, Optional, Union
from fastapi import Response, status
from pydantic import BaseModel


class ApiResponse(BaseModel):
    """アプリ全体で統一的に利用するAPIレスポンスモデル"""

    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None

    @classmethod
    def ok(
        cls,
        data: Any = None,
        message: Optional[str] = None,
        response: Optional[Response] = None,
        status_code: int = status.HTTP_200_OK,
    ) -> "ApiResponse":
        """
        正常レスポンスを生成。
        必要に応じてHTTPステータスコードを変更できる。
        """
        if response:
            response.status_code = status_code
        return cls(success=True, message=message, data=data)

    @classmethod
    def created(
        cls,
        data: Any = None,
        message: Optional[str] = "Created successfully",
        response: Optional[Response] = None,
    ) -> "ApiResponse":
        """POST時などリソース作成成功用"""
        if response:
            response.status_code = status.HTTP_201_CREATED
        return cls(success=True, message=message, data=data)

    @classmethod
    def error(
        cls,
        message: str,
        data: Any = None,
        response: Optional[Response] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> "ApiResponse":
        """
        エラーレスポンスを生成。
        FastAPIのResponseを渡せばHTTPステータスも自動設定。
        """
        if response:
            response.status_code = status_code
        return cls(success=False, message=message, data=data)

    @classmethod
    def unauthorized(
        cls,
        message: str = "Unauthorized",
        response: Optional[Response] = None,
    ) -> "ApiResponse":
        """認証エラー用のヘルパー"""
        if response:
            response.status_code = status.HTTP_401_UNAUTHORIZED
        return cls(success=False, message=message)

    @classmethod
    def not_found(
        cls,
        message: str = "Resource not found",
        response: Optional[Response] = None,
    ) -> "ApiResponse":
        """404用のヘルパー"""
        if response:
            response.status_code = status.HTTP_404_NOT_FOUND
        return cls(success=False, message=message)
