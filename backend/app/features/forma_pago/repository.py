# features/forma_pago/repository.py - FormaPagoRepository

from app.core.repository import BaseRepository
from app.features.forma_pago.models import FormaPago


class FormaPagoRepository(BaseRepository[FormaPago]):
    """Repositorio de formas de pago."""

    def __init__(self):
        super().__init__(FormaPago)
