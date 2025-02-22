from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI, status
from typing import Any, Callable

# create the exception classes below
class UserException(Exception):
    """
    Raised when the user already exists.
    """
    pass


class UserAlreadyExists(UserException):
    """
    Raised when the user already exists.
    """
    pass


class InvalidCredentials(UserException):
    """
    Raised when the provided credentials are invalid.
    """
    pass


class InvalidToken(UserException):
    """
    Raised when the provided token is invalid.
    """
    pass


class AccessTokenRequired(UserException):
    """
    Raised when the user is not authenticated or provided refresh token instead of access token.
    """


class RefreshTokenRequired(UserException):
    """
    Raised when the user is not authenticated or provided access token instead of refresh token.
    """
    pass

# create the exception handler below
def create_exception_handler(status_code: int,
                             initial_detail: Any) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: UserAlreadyExists):
        return JSONResponse(
            content=initial_detail,
            status_code=status_code
        )

    return exception_handler


# register all exceptions
def register_all_exceptions(app: FastAPI):
    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "User with email already exists",
                "error_code": "user_exists"
            }
        )
    )

    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Invalid credentials",
                "error_code": "invalid_credentials"
            }
        )
    )

    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Invalid token",
                "resolution": "Please get a new token",
                "error_code": "invalid_token"
            }
        )
    )

    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Access token required",
                "resolution": "Please provide an access token",
                "error_code": "access_token_required"
            }
        )
    )

    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Refresh token required",
                "resolution": "Please provide a refresh token",
                "error_code": "refresh_token_required"
            }
        )
    )