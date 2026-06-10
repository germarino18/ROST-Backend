# features/direccion/router.py - Endpoints CRUD de direcciones de entrega
# Todos scoped al usuario autenticado
# GET    /api/v1/direcciones → Lista direcciones del usuario
# GET    /api/v1/direcciones/{id} → Obtiene dirección del usuario
# POST   /api/v1/direcciones → Crea dirección para el usuario
# PUT    /api/v1/direcciones/{id} → Actualiza dirección del usuario
# DELETE /api/v1/direcciones/{id} → Soft delete de dirección del usuario
# PATCH  /api/v1/direcciones/{id}/principal → Marca como principal

from typing import List
from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from app.db.database import get_session
from app.core.uow import UnitOfWork
from app.core.dependencies import get_current_user
from app.features.auth.models import Usuario
from app.features.direccion.schemas import DireccionCreate, DireccionRead, DireccionUpdate
from app.features.direccion.service import DireccionService
from app.features.direccion.repository import DireccionRepository

router = APIRouter(prefix="/api/v1/direcciones", tags=["Direcciones"])


@router.get("", response_model=List[DireccionRead])
def listar_direcciones(
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """GET /api/v1/direcciones - Lista direcciones del usuario autenticado."""
    with UnitOfWork(session) as uow:
        repo = DireccionRepository()
        service = DireccionService(uow, repo)
        return service.get_all(current_user.id)


@router.get("/{id}", response_model=DireccionRead)
def obtener_direccion(
    id: int,
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """GET /api/v1/direcciones/{id} - Obtiene dirección del usuario autenticado."""
    with UnitOfWork(session) as uow:
        repo = DireccionRepository()
        service = DireccionService(uow, repo)
        return service.get_by_id(id, current_user.id)


@router.post("", response_model=DireccionRead, status_code=status.HTTP_201_CREATED)
def crear_direccion(
    data: DireccionCreate,
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """POST /api/v1/direcciones - Crea una nueva dirección para el usuario autenticado."""
    with UnitOfWork(session) as uow:
        repo = DireccionRepository()
        service = DireccionService(uow, repo)
        return service.create(data, current_user.id)


@router.put("/{id}", response_model=DireccionRead)
def actualizar_direccion(
    id: int,
    data: DireccionUpdate,
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """PUT /api/v1/direcciones/{id} - Actualiza dirección del usuario autenticado."""
    with UnitOfWork(session) as uow:
        repo = DireccionRepository()
        service = DireccionService(uow, repo)
        return service.update(id, data, current_user.id)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_direccion(
    id: int,
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """DELETE /api/v1/direcciones/{id} - Soft delete de dirección del usuario autenticado."""
    with UnitOfWork(session) as uow:
        repo = DireccionRepository()
        service = DireccionService(uow, repo)
        return service.delete(id, current_user.id)


@router.patch("/{id}/principal", response_model=DireccionRead)
def marcar_principal(
    id: int,
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """PATCH /api/v1/direcciones/{id}/principal - Marca dirección como principal.
    Desmarca cualquier otra dirección principal del usuario."""
    with UnitOfWork(session) as uow:
        repo = DireccionRepository()
        service = DireccionService(uow, repo)
        return service.set_principal(id, current_user.id)
