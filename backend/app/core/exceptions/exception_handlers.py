
from datetime import datetime, timezone

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions.custom_exceptions import (
    AppError,
    RateLimitExceededError,
)
from app.core.logger import get_logger

logger = get_logger("app.exceptions")


def _build_error_response(
    *,
    code: str,
    message: str,
    status_code: int,
    request_id: str | None = None,
    extra: dict | None = None,
) -> JSONResponse:
    body = {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    }
    if extra:
        body["error"].update(extra)

    return JSONResponse(status_code=status_code, content=body)


def _get_request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


# ─── HANDLER 1: Excepciones de dominio (AppError) ─────────────────────────────

async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    request_id = _get_request_id(request)

    if exc.status_code >= 500:
        logger.error(
            "[%s] AppError %d %s: %s",
            request_id, exc.status_code, exc.code, exc.message,
        )
    else:
        logger.warning(
            "[%s] AppError %d %s: %s",
            request_id, exc.status_code, exc.code, exc.message,
        )

    response = _build_error_response(
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        request_id=request_id,
    )

    # Si es rate limit, agregamos el header Retry-After.
    # Estándar HTTP: indica cuántos segundos esperar.
    if isinstance(exc, RateLimitExceededError):
        response.headers["Retry-After"] = str(exc.retry_after)

    return response


# ─── HANDLER 2: HTTPException (404 manual, 401, 403, etc.) ────────────────────

async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    request_id = _get_request_id(request)
    logger.warning(
        "[%s] HTTPException %d: %s",
        request_id, exc.status_code, exc.detail,
    )

    # Mapeo de status_code → código interno.
    # Esto da consistencia con los códigos de AppError.
    code_map = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        405: "method_not_allowed",
        409: "conflict",
        422: "validation_error",
        429: "rate_limit_exceeded",
        500: "internal_error",
    }
    code = code_map.get(exc.status_code, "http_error")

    return _build_error_response(
        code=code,
        message=str(exc.detail),
        status_code=exc.status_code,
        request_id=request_id,
    )


# ─── HANDLER 3: Errores de validación de Pydantic (422) ──────────────────────

async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    request_id = _get_request_id(request)

    # Transformamos cada error a un formato simple y útil para el frontend.
    errors = []
    for err in exc.errors():
        # err["loc"] es una tupla: ("body", "email") o ("path", "id").
        # Lo convertimos a un path string: "body.email" o "path.id".
        location = ".".join(str(x) for x in err.get("loc", []))
        errors.append({
            "field": location,
            "message": err.get("msg", "Error de validación"),
            "type": err.get("type", "validation_error"),
        })

    logger.info(
        "[%s] Validation error: %d errores en %s",
        request_id, len(errors), request.url.path,
    )

    return _build_error_response(
        code="validation_error",
        message="Los datos enviados no son válidos",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        request_id=request_id,
        extra={"fields": errors},
    )


# ─── HANDLER 4: Errores de base de datos ──────────────────────────────────────

async def sqlalchemy_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    request_id = _get_request_id(request)

    if isinstance(exc, IntegrityError):
        logger.warning(
            "[%s] IntegrityError en %s: %s",
            request_id, request.url.path, str(exc.orig),
        )
        return _build_error_response(
            code="duplicate_resource",
            message="La operación viola una restricción de unicidad o integridad.",
            status_code=status.HTTP_409_CONFLICT,
            request_id=request_id,
        )
        
    logger.error(
        "[%s] SQLAlchemyError en %s: %s",
        request_id, request.url.path, repr(exc),
        exc_info=True,  # Incluye el stack trace completo en el log.
    )
    return _build_error_response(
        code="database_error",
        message="Error de base de datos. Contacta al administrador.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        request_id=request_id,
    )


# ─── HANDLER 5: Catch-all (cualquier excepción no manejada) ───────────────────

async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = _get_request_id(request)
    logger.critical(
        "[%s] UNHANDLED EXCEPTION en %s: %s",
        request_id, request.url.path, repr(exc),
        exc_info=True,
    )
    return _build_error_response(
        code="internal_error",
        message="Error interno del servidor. El equipo ha sido notificado.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        request_id=request_id,
    )


# ─── FUNCIÓN DE REGISTRO ─────────────────────────────────────────────────────

def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    
    app.add_exception_handler(Exception, unhandled_exception_handler)
