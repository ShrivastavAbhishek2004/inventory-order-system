from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)


# ── Custom Exception Classes ──────────────────────────────────────────────────

class NotFoundError(HTTPException):
    """Raised when a requested resource does not exist."""
    def __init__(self, resource: str, resource_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with id {resource_id} not found.",
        )


class DuplicateError(HTTPException):
    """Raised when a unique constraint is violated (e.g. duplicate SKU or email)."""
    def __init__(self, resource: str, field: str, value: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{resource} with {field} '{value}' already exists.",
        )


class InsufficientStockError(HTTPException):
    """Raised when an order exceeds available product stock."""
    def __init__(self, product_name: str, available: int, requested: int):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Insufficient stock for '{product_name}'. "
                f"Available: {available}, Requested: {requested}."
            ),
        )


class ValidationError(HTTPException):
    """Raised for business rule violations (e.g. negative quantity)."""
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=message,
        )


# ── Global Exception Handlers ─────────────────────────────────────────────────
# These are registered on the FastAPI app in main.py.
# They catch exceptions and return consistent JSON error responses.

async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handles Pydantic validation errors (e.g. wrong data types in request body).
    Returns a clear, structured error message.
    """
    errors = []
    for error in exc.errors():
        field = " → ".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"],
        })

    logger.warning(f"Validation error on {request.url}: {errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Input validation failed. Please check your request data.",
            "errors": errors,
        },
    )


async def http_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    """
    Handles all HTTPExceptions with a consistent JSON format.
    """
    logger.warning(f"HTTP {exc.status_code} on {request.url}: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
        },
    )


async def integrity_error_handler(
    request: Request, exc: IntegrityError
) -> JSONResponse:
    """
    Handles SQLAlchemy database integrity errors (e.g. duplicate unique field).
    Prevents raw database error messages from leaking to the client.
    """
    logger.error(f"Database integrity error on {request.url}: {exc}")

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "success": False,
            "message": "A record with this data already exists.",
        },
    )


async def global_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    Catches any unexpected errors so the API never crashes with a raw 500.
    """
    logger.error(f"Unexpected error on {request.url}: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected server error occurred. Please try again later.",
        },
    )