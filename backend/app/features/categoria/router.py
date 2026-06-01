# features/categoria/router.py - Endpoints CRUD de categorías
# GET   /api/v1/categorias → Lista categorías (público, filtros: q, parent_id)
# GET   /api/v1/categorias/{id} → Obtiene categoría por ID (público)
# POST  /api/v1/categorias → Crea categoría (requiere ADMIN)
# PATCH /api/v1/categorias/{id} → Actualiza categoría (requiere ADMIN)
# DELETE /api/v1/categorias/{id} → Soft delete (requiere ADMIN)

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session
from app.db.database import get_session
from app.core.uow import UnitOfWork
from app.core.dependencies import require_role
from app.features.categoria.schemas import CategoriaCreate, CategoriaRead, CategoriaUpdate
from app.features.categoria.service import CategoriaService
from app.features.categoria.repository import CategoriaRepository

router = APIRouter(prefix="/api/v1/categorias", tags=["Categorías"])


def get_service(session: Session = Depends(get_session)) -> CategoriaService:
    """Inyecta CategoriaService con UnitOfWork y CategoriaRepository."""
    uow = UnitOfWork(session)
    repo = CategoriaRepository()
    return CategoriaService(uow, repo)


@router.get("", response_model=List[CategoriaRead])
def listar_categorias(
    q: Optional[str] = Query(None, description="Buscar por nombre"),
    parent_id: Optional[int] = Query(None, description="Filtrar por categoría padre"),
    service: CategoriaService = Depends(get_service),
):
    """GET /api/v1/categorias - Lista categorías activas (público).
    Filtros: q (nombre), parent_id (categoría padre)."""
    return service.get_all(q=q, parent_id=parent_id)


@router.get("/{id}", response_model=CategoriaRead)
def obtener_categoria(id: int, service: CategoriaService = Depends(get_service)):
    """GET /api/v1/categorias/{id} - Obtiene categoría por ID (público)."""
    return service.get_by_id(id)


@router.post("", response_model=CategoriaRead, status_code=status.HTTP_201_CREATED)
def crear_categoria(
    data: CategoriaCreate,
    service: CategoriaService = Depends(get_service),
    _=Depends(require_role(["ADMIN"])),
):
    """POST /api/v1/categorias - Crea una nueva categoría.
    Requiere: rol ADMIN. Acepta parent_id para jerarquía."""
    return service.create(data)


@router.patch("/{id}", response_model=CategoriaRead)
def actualizar_categoria(
    id: int,
    data: CategoriaUpdate,
    service: CategoriaService = Depends(get_service),
    _=Depends(require_role(["ADMIN"])),
):
    """PATCH /api/v1/categorias/{id} - Actualiza parcialmente una categoría.
    Requiere: rol ADMIN."""
    return service.update(id, data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(
    id: int,
    service: CategoriaService = Depends(get_service),
    _=Depends(require_role(["ADMIN"])),
):
    """DELETE /api/v1/categorias/{id} - Soft delete de categoría.
    Requiere: rol ADMIN."""
    return service.delete(id)
