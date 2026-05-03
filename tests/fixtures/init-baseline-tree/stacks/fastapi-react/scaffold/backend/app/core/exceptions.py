"""Custom HTTP exception classes for consistent error responses.

Use these instead of raising fastapi.HTTPException directly so that
error handling is uniform across the application.

Example:
    from app.core.exceptions import NotFoundError
    raise NotFoundError(detail="User not found")
"""

from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    """Resource not found (404)."""

    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class PermissionDeniedError(HTTPException):
    """Insufficient permissions (403)."""

    def __init__(self, detail: str = "Permission denied") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class BadRequestError(HTTPException):
    """Invalid request data (400)."""

    def __init__(self, detail: str = "Bad request") -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
