# core/dependencies.py - Dependencias de FastAPI para autenticación y autorización
# get_current_user: extrae el usuario desde la cookie "access_token" (JWT)
# require_role: factory que retorna un dependency checker de roles
# require_admin: atajo para require_role("ADMIN")

from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session
from app.db.database import get_session
from app.core.security import decode_access_token
from app.features.auth.models import Usuario


async def get_current_user(
    request: Request,
    session: Session = Depends(get_session),
) -> Usuario:
    """Extrae el usuario autenticado desde la cookie 'access_token'.
    Lanza: 401 si no hay token, es inválido, o el usuario está inactivo/eliminado."""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
        )
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )
    user = session.get(Usuario, user_id)
    if not user or user.deleted_at is not None or not user.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
        )
    return user


def require_role(rol_codigo: str):
    """Factory que retorna un dependency checker de un solo rol.
    Lanza: 403 si el usuario no tiene el rol requerido."""
    async def role_checker(
        current_user: Usuario = Depends(get_current_user),
    ):
        if current_user.rol_codigo != rol_codigo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para esta acción",
            )
        return current_user
    return role_checker


require_admin = require_role("ADMIN")


def require_any_role(*roles: str):
    """Factory que retorna un dependency checker de múltiples roles.
    Lanza: 403 si el usuario no tiene ninguno de los roles permitidos."""
    async def role_checker(
        current_user: Usuario = Depends(get_current_user),
    ):
        if current_user.rol_codigo not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para esta acción",
            )
        return current_user
    return role_checker
