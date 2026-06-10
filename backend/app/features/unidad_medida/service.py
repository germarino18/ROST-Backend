# features/unidad_medida/service.py - Servicio de unidades de medida
# NO contiene consultas ORM directas — delega en UnidadMedidaRepository.

from typing import List, Optional
from app.core.uow import UnitOfWork
from app.features.unidad_medida.models import UnidadMedida
from app.features.unidad_medida.schemas import UnidadMedidaCreate, UnidadMedidaUpdate
from app.features.unidad_medida.repository import UnidadMedidaRepository


class UnidadMedidaService:
    """Servicio de unidades de medida. Delega en el repositorio."""

    def __init__(self, uow: UnitOfWork, repo: UnidadMedidaRepository):
        self.uow = uow
        self.repo = repo

    def get_all(self, tipo: Optional[str] = None) -> List[UnidadMedida]:
        return self.repo.get_all_by_tipo(self.uow.session, tipo=tipo)

    def get_by_id(self, id: int) -> UnidadMedida:
        return self.repo.get_by_id_or_404(self.uow.session, id)

    def create(self, schema: UnidadMedidaCreate) -> UnidadMedida:
        obj = self.repo.create(self.uow.session, **schema.model_dump())
        return obj

    def update(self, id: int, schema: UnidadMedidaUpdate) -> UnidadMedida:
        session = self.uow.session
        obj = self.repo.get_by_id_or_404(session, id)
        data = schema.model_dump(exclude_unset=True)
        if data:
            obj = self.repo.update(session, obj, **data)
        return obj

    def delete(self, id: int) -> None:
        obj = self.repo.get_by_id_or_404(self.uow.session, id)
        self.repo.delete(self.uow.session, obj)
