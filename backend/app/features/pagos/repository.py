# features/pagos/repository.py - PagoRepository

from typing import Optional
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.features.pagos.models import Pago


class PagoRepository(BaseRepository[Pago]):
    """Repositorio de pagos. Hereda CRUD de BaseRepository."""

    def __init__(self):
        super().__init__(Pago)

    def get_by_pedido_id(self, session: Session, pedido_id: int) -> Optional[Pago]:
        """Obtiene un pago por ID de pedido."""
        return session.exec(
            select(Pago).where(Pago.pedido_id == pedido_id)
        ).first()

    def get_by_mp_payment_id(self, session: Session, mp_payment_id: int) -> Optional[Pago]:
        """Obtiene un pago por ID de MercadoPago."""
        return session.exec(
            select(Pago).where(Pago.mp_payment_id == mp_payment_id)
        ).first()

    def get_by_external_reference(self, session: Session, external_reference: str) -> Optional[Pago]:
        """Obtiene un pago por external_reference."""
        return session.exec(
            select(Pago).where(Pago.external_reference == external_reference)
        ).first()
