# features/ingrediente/repository.py - IngredienteRepository
# Consultas específicas: búsqueda textual, filtro por alérgeno.

from typing import List, Optional
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.features.ingrediente.models import Ingrediente


class IngredienteRepository(BaseRepository[Ingrediente]):
    """Repositorio de ingredientes."""

    def __init__(self):
        super().__init__(Ingrediente)

    def get_all_filtered(
        self,
        session: Session,
        q: Optional[str] = None,
        es_alergeno: Optional[bool] = None,
    ) -> List[Ingrediente]:
        """Lista ingredientes con filtros opcionales."""
        stmt = select(Ingrediente)
        if q:
            stmt = stmt.where(Ingrediente.nombre.ilike(f"%{q}%"))
        if es_alergeno is not None:
            stmt = stmt.where(Ingrediente.es_alergeno == es_alergeno)
        return list(session.exec(stmt).all())
