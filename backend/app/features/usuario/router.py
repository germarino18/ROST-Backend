# features/usuario/router.py - Endpoints de administración de usuarios
# GET  /api/v1/admin/roles → Lista todos los roles del sistema
# GET  /api/v1/admin/usuarios → Lista usuarios con filtro opcional por rol
# PATCH /api/v1/admin/usuarios/{id} → Actualiza usuario (nombre, email, activo)
# POST /api/v1/admin/usuarios/{id}/roles → Asigna un rol a un usuario
# DELETE /api/v1/admin/usuarios/{id}/roles/{rol_codigo} → Remueve un rol

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session
from app.db.database import get_session
from app.core.uow import UnitOfWork
from app.core.dependencies import require_admin
from app.features.usuario.schemas import AdminUserRead, AdminUserUpdate, AdminRolAsignar
from app.features.usuario.service import AdminService
from app.features.usuario.repository import UsuarioRepository

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


def get_service(session: Session = Depends(get_session)) -> AdminService:
    """Inyecta AdminService con UnitOfWork y UsuarioRepository."""
    uow = UnitOfWork(session)
    repo = UsuarioRepository()
    return AdminService(uow, repo)


@router.get("/roles")
def listar_roles(
    service: AdminService = Depends(get_service),
    _=Depends(require_admin),
):
    """GET /api/v1/admin/roles - Lista todos los roles del sistema.
    Requiere: rol ADMIN."""
    return service.listar_roles()


@router.get("/usuarios", response_model=List[AdminUserRead])
def listar_usuarios(
    rol: Optional[str] = Query(None, description="Filtrar por rol"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    service: AdminService = Depends(get_service),
    _=Depends(require_admin),
):
    """GET /api/v1/admin/usuarios - Lista usuarios activos (paginado).
    Requiere: rol ADMIN.
    Query params: rol (filtrar por código de rol), skip, limit."""
    return service.listar_usuarios(rol=rol, skip=skip, limit=limit)


@router.patch("/usuarios/{id}", response_model=AdminUserRead)
def actualizar_usuario(
    id: int,
    data: AdminUserUpdate,
    service: AdminService = Depends(get_service),
    _=Depends(require_admin),
):
    """PATCH /api/v1/admin/usuarios/{id} - Actualiza datos de un usuario.
    Requiere: rol ADMIN. Campos: nombre, email, activo."""
    return service.actualizar_usuario(id, data)


@router.post("/usuarios/{id}/roles")
def asignar_rol(
    id: int,
    data: AdminRolAsignar,
    service: AdminService = Depends(get_service),
    _=Depends(require_admin),
):
    """POST /api/v1/admin/usuarios/{id}/roles - Asigna un rol a un usuario.
    Requiere: rol ADMIN."""
    return service.asignar_rol(id, data.rol_codigo)


@router.delete("/usuarios/{id}/roles/{rol_codigo}")
def remover_rol(
    id: int,
    rol_codigo: str,
    service: AdminService = Depends(get_service),
    _=Depends(require_admin),
):
    """DELETE /api/v1/admin/usuarios/{id}/roles/{rol_codigo} - Remueve un rol.
    Requiere: rol ADMIN."""
    return service.remover_rol(id, rol_codigo)
