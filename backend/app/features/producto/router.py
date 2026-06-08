# features/producto/router.py - Endpoints CRUD de productos
# GET   /api/v1/productos → Lista productos (público, filtros: q, categoria_id, disponible)
# GET   /api/v1/productos/{id} → Obtiene producto por ID (público)
# POST  /api/v1/productos → Crea producto (requiere ADMIN)
# PATCH /api/v1/productos/{id} → Actualiza producto (requiere ADMIN o STOCK)
# DELETE /api/v1/productos/{id} → Soft delete (requiere ADMIN)
# PATCH /api/v1/productos/{id}/disponibilidad → Cambia disponibilidad (ADMIN o STOCK)

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session
from app.db.database import get_session
from app.core.uow import UnitOfWork
from app.core.dependencies import require_role, require_any_role
from app.features.producto.schemas import ProductoCreate, ProductoRead, ProductoUpdate
from app.features.producto.service import ProductoService
from app.features.producto.repository import ProductoRepository

router = APIRouter(prefix="/api/v1/productos", tags=["Productos"])


def get_service(session: Session = Depends(get_session)) -> ProductoService:
    uow = UnitOfWork(session)
    repo = ProductoRepository()
    return ProductoService(uow, repo)


@router.get("", response_model=List[ProductoRead])
def listar_productos(
    q: Optional[str] = Query(None, description="Buscar por nombre"),
    categoria_id: Optional[int] = Query(None, description="Filtrar por categoría"),
    disponible: Optional[bool] = Query(None, description="Filtrar por disponibilidad"),
    service: ProductoService = Depends(get_service),
):
    """GET /api/v1/productos - Lista productos activos (público).
    Filtros: q (nombre), categoria_id, disponible."""
    return service.get_all(q=q, categoria_id=categoria_id, disponible=disponible)


@router.get("/{id}", response_model=ProductoRead)
def obtener_producto(id: int, service: ProductoService = Depends(get_service)):
    """GET /api/v1/productos/{id} - Obtiene un producto por ID (público)."""
    return service.get_by_id(id)


@router.post("", response_model=ProductoRead, status_code=status.HTTP_201_CREATED)
def crear_producto(
    data: ProductoCreate,
    service: ProductoService = Depends(get_service),
    _=Depends(require_role("ADMIN")),
):
    """POST /api/v1/productos - Crea un nuevo producto.
    Requiere: rol ADMIN. Acepta categorías e ingredientes en el body."""
    return service.create(data)


@router.patch("/{id}", response_model=ProductoRead)
def actualizar_producto(
    id: int,
    data: ProductoUpdate,
    service: ProductoService = Depends(get_service),
    _=Depends(require_any_role("ADMIN", "STOCK")),
):
    """PATCH /api/v1/productos/{id} - Actualiza parcialmente un producto.
    Requiere: ADMIN o STOCK. Reemplaza relaciones si se envían."""
    return service.update(id, data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(
    id: int,
    service: ProductoService = Depends(get_service),
    _=Depends(require_role("ADMIN")),
):
    """DELETE /api/v1/productos/{id} - Soft delete de producto.
    Requiere: rol ADMIN."""
    return service.delete(id)


@router.patch("/{id}/disponibilidad", response_model=ProductoRead)
def cambiar_disponibilidad(
    id: int,
    disponible: bool = Query(..., description="Nuevo estado de disponibilidad"),
    service: ProductoService = Depends(get_service),
    _=Depends(require_any_role("ADMIN", "STOCK")),
):
    """PATCH /api/v1/productos/{id}/disponibilidad - Cambia disponibilidad.
    Requiere: ADMIN o STOCK. Útil para toggle rápido sin enviar todo el producto."""
    return service.cambiar_disponibilidad(id, disponible)
