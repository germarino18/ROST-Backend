# features/categoria/repository.py - CategoriaRepository
# Consultas específicas sobre categorías: búsqueda textual, filtro por padre,
# verificación de soft delete.

from datetime import datetime, timezone
from typing import List, Optional
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.features.categoria.models import Categoria


class CategoriaRepository(BaseRepository[Categoria]):
    """Repositorio de categorías. Hereda BaseRepository y agrega
    métodos específicos con filtros y soft delete."""

    def __init__(self):
        super().__init__(Categoria)

    def get_all_active(
        self,
        session: Session,
        q: Optional[str] = None,
        parent_id: Optional[int] = None,
    ) -> List[Categoria]:
        """Lista categorías activas (sin soft delete) con filtros opcionales."""
        stmt = select(Categoria).where(Categoria.deleted_at.is_(None))
        if q:
            stmt = stmt.where(Categoria.nombre.ilike(f"%{q}%"))
        if parent_id is not None:
            stmt = stmt.where(Categoria.parent_id == parent_id)
        return list(session.exec(stmt).all())

    def get_by_id_active(self, session: Session, id: int) -> Optional[Categoria]:
        """Obtiene categoría por ID si no está eliminada (soft delete)."""
        obj = self.get_by_id(session, id)
        if obj and obj.deleted_at is not None:
            return None
        return obj

    def soft_delete(self, session: Session, obj: Categoria) -> None:
        """Marca deleted_at en lugar de eliminar el registro."""
        obj.deleted_at = datetime.now(timezone.utc)
        session.add(obj)
        session.flush()
