# features/forma_pago/service.py - Servicio de formas de pago

from typing import List
from app.core.uow import UnitOfWork
from app.features.forma_pago.models import FormaPago
from app.features.forma_pago.schemas import FormaPagoCreate
from app.features.forma_pago.repository import FormaPagoRepository


class FormaPagoService:
    """Servicio de formas de pago."""

    def __init__(self, uow: UnitOfWork, repo: FormaPagoRepository):
        self.uow = uow
        self.repo = repo

    def get_all(self) -> List[FormaPago]:
        return self.repo.get_all(self.uow.session)

    def create(self, schema: FormaPagoCreate) -> FormaPago:
        obj = self.repo.create(self.uow.session, **schema.model_dump())
        self.uow.commit()
        return obj
