# features/direccion/repository.py - DireccionRepository
# Consultas scoped por usuario: cada dirección pertenece a un usuario.

from datetime import datetime, timezone
from typing import List, Optional
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.features.direccion.models import DireccionEntrega


class DireccionRepository(BaseRepository[DireccionEntrega]):
    """Repositorio de direcciones de entrega."""

    def __init__(self):
        super().__init__(DireccionEntrega)

    def get_all_by_usuario(
        self, session: Session, usuario_id: int
    ) -> List[DireccionEntrega]:
        """Lista direcciones activas de un usuario, ordenadas: principal primero."""
        stmt = (
            select(DireccionEntrega)
            .where(
                DireccionEntrega.usuario_id == usuario_id,
                DireccionEntrega.deleted_at.is_(None),
            )
            .order_by(
                DireccionEntrega.es_principal.desc(),
                DireccionEntrega.created_at.desc(),
            )
        )
        return list(session.exec(stmt).all())

    def get_by_id_and_usuario(
        self, session: Session, id: int, usuario_id: int
    ) -> Optional[DireccionEntrega]:
        """Obtiene dirección por ID, validando que pertenezca al usuario."""
        return session.exec(
            select(DireccionEntrega).where(
                DireccionEntrega.id == id,
                DireccionEntrega.usuario_id == usuario_id,
                DireccionEntrega.deleted_at.is_(None),
            )
        ).first()

    def unset_all_principal(
        self, session: Session, usuario_id: int
    ) -> None:
        """Desmarca todas las direcciones principales de un usuario."""
        current = session.exec(
            select(DireccionEntrega).where(
                DireccionEntrega.usuario_id == usuario_id,
                DireccionEntrega.es_principal == True,
                DireccionEntrega.deleted_at.is_(None),
            )
        ).all()
        for addr in current:
            addr.es_principal = False
            session.add(addr)

    def soft_delete(self, session: Session, obj: DireccionEntrega) -> None:
        """Marca deleted_at en lugar de eliminar."""
        obj.deleted_at = datetime.now(timezone.utc)
        session.add(obj)
        session.flush()
