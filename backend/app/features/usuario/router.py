# features/usuario/router.py - Endpoints de administración de usuarios
# GET  /api/v1/admin/roles → Lista todos los roles del sistema
# GET  /api/v1/admin/usuarios → Lista usuarios con filtro opcional por rol
# POST /api/v1/admin/usuarios → Crea usuario con rol único
# PATCH /api/v1/admin/usuarios/{id} → Actualiza usuario (nombre, email, activo)

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session
from app.db.database import get_session
from app.core.uow import UnitOfWork
from app.core.dependencies import require_admin
from app.features.usuario.schemas import AdminUserCreate, AdminUserRead, AdminUserUpdate
from app.features.usuario.service import AdminService
from app.features.usuario.repository import UsuarioRepository

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


@router.get("/roles")
def listar_roles(
    session: Session = Depends(get_session),
    _=Depends(require_admin),
):
    """GET /api/v1/admin/roles - Lista todos los roles del sistema.
    Requiere: rol ADMIN."""
    with UnitOfWork(session) as uow:
        repo = UsuarioRepository()
        service = AdminService(uow, repo)
        return service.listar_roles()


@router.get("/usuarios", response_model=List[AdminUserRead])
def listar_usuarios(
    rol: Optional[str] = Query(None, description="Filtrar por rol"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
    _=Depends(require_admin),
):
    """GET /api/v1/admin/usuarios - Lista usuarios activos (paginado).
    Requiere: rol ADMIN.
    Query params: rol (filtrar por código de rol), skip, limit."""
    with UnitOfWork(session) as uow:
        repo = UsuarioRepository()
        service = AdminService(uow, repo)
        return service.listar_usuarios(rol=rol, skip=skip, limit=limit)


@router.post("/usuarios", response_model=AdminUserRead, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    data: AdminUserCreate,
    session: Session = Depends(get_session),
    _=Depends(require_admin),
):
    """POST /api/v1/admin/usuarios - Crea un usuario con rol específico.
    Requiere: ADMIN."""
    with UnitOfWork(session) as uow:
        repo = UsuarioRepository()
        service = AdminService(uow, repo)
        return service.crear_usuario(data)


@router.patch("/usuarios/{id}", response_model=AdminUserRead)
def actualizar_usuario(
    id: int,
    data: AdminUserUpdate,
    session: Session = Depends(get_session),
    _=Depends(require_admin),
):
    """PATCH /api/v1/admin/usuarios/{id} - Actualiza datos de un usuario.
    Requiere: rol ADMIN. Campos: nombre, email, activo."""
    with UnitOfWork(session) as uow:
        repo = UsuarioRepository()
        service = AdminService(uow, repo)
        return service.actualizar_usuario(id, data)
