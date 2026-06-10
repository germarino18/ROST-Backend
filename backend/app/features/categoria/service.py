# features/categoria/service.py - Servicio de categorías
# Hereda lógica de negocio sobre CategoriaRepository.
# NO contiene consultas ORM directas — delega en CategoriaRepository.

from datetime import datetime, timezone
from typing import List, Optional
from sqlmodel import Session
from fastapi import HTTPException
from app.core.uow import UnitOfWork
from app.features.categoria.models import Categoria
from app.features.categoria.schemas import CategoriaCreate, CategoriaUpdate
from app.features.categoria.repository import CategoriaRepository


class CategoriaService:
    """Servicio de categorías. Toda la lógica de negocio vive aquí.
    No tiene session.exec() ni session.add() — delega en el repositorio."""

    def __init__(self, uow: UnitOfWork, repo: CategoriaRepository):
        self.uow = uow
        self.repo = repo

    def get_all(
        self,
        q: Optional[str] = None,
        parent_id: Optional[int] = None,
    ) -> List[Categoria]:
        """Lista categorías activas con filtros opcionales."""
        return self.repo.get_all_active(self.uow.session, q=q, parent_id=parent_id)

    def get_by_id(self, id: int) -> Categoria:
        """Obtiene categoría por ID. Lanza 404 si no existe o está eliminada."""
        obj = self.repo.get_by_id_active(self.uow.session, id)
        if not obj:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        return obj

    def create(self, schema: CategoriaCreate) -> Categoria:
        session = self.uow.session
        data = schema.model_dump()
        obj = self.repo.create(session, **data)
        return obj

    def update(self, id: int, schema: CategoriaUpdate) -> Categoria:
        session = self.uow.session
        obj = self.get_by_id(id)
        data = schema.model_dump(exclude_unset=True)
        if data:
            obj = self.repo.update(session, obj, **data)
            obj.updated_at = datetime.now(timezone.utc)
            session.add(obj)
            session.flush()
            session.refresh(obj)
        return obj

    def delete(self, id: int) -> None:
        """Soft delete: marca deleted_at en lugar de eliminar."""
        obj = self.get_by_id(id)
        self.repo.soft_delete(self.uow.session, obj)
