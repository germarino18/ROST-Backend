# features/unidad_medida/repository.py - UnidadMedidaRepository
# Consultas específicas para unidades de medida.

from typing import List, Optional
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.features.unidad_medida.models import UnidadMedida


class UnidadMedidaRepository(BaseRepository[UnidadMedida]):
    """Repositorio de unidades de medida."""

    def __init__(self):
        super().__init__(UnidadMedida)

    def get_all_by_tipo(self, session: Session, tipo: Optional[str] = None) -> List[UnidadMedida]:
        """Lista unidades de medida, opcionalmente filtradas por tipo."""
        stmt = select(UnidadMedida)
        if tipo:
            stmt = stmt.where(UnidadMedida.tipo == tipo)
        return list(session.exec(stmt).all())
