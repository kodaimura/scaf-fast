from app.core.error import AppError, ErrorCode


def resolve_login_id(mode: str, login_id: str | None, email: str | None) -> str:
    if mode == "email":
        if not email:
            raise AppError(code=ErrorCode.EMAIL_REQUIRED)
        return email

    if mode == "login_id":
        if not login_id:
            raise AppError(code=ErrorCode.LOGIN_ID_REQUIRED)
        return login_id

    raise AppError(code=ErrorCode.INVALID_STATE)
