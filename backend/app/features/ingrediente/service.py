# features/ingrediente/service.py - Servicio de ingredientes
# NO contiene consultas ORM directas — delega en IngredienteRepository.

from typing import List, Optional
from app.core.uow import UnitOfWork
from app.features.ingrediente.models import Ingrediente
from app.features.ingrediente.schemas import IngredienteCreate, IngredienteUpdate
from app.features.ingrediente.repository import IngredienteRepository


class IngredienteService:
    """Servicio de ingredientes. Delega en el repositorio."""

    def __init__(self, uow: UnitOfWork, repo: IngredienteRepository):
        self.uow = uow
        self.repo = repo

    def get_all(
        self, q: Optional[str] = None, es_alergeno: Optional[bool] = None
    ) -> List[Ingrediente]:
        return self.repo.get_all_filtered(self.uow.session, q=q, es_alergeno=es_alergeno)

    def get_by_id(self, id: int) -> Ingrediente:
        return self.repo.get_by_id_or_404(self.uow.session, id)

    def create(self, schema: IngredienteCreate) -> Ingrediente:
        obj = self.repo.create(self.uow.session, **schema.model_dump())
        self.uow.commit()
        return obj

    def update(self, id: int, schema: IngredienteUpdate) -> Ingrediente:
        session = self.uow.session
        obj = self.repo.get_by_id_or_404(session, id)
        data = schema.model_dump(exclude_unset=True)
        if data:
            obj = self.repo.update(session, obj, **data)
        self.uow.commit()
        return obj

    def delete(self, id: int) -> None:
        obj = self.repo.get_by_id_or_404(self.uow.session, id)
        self.repo.delete(self.uow.session, obj)
        self.uow.commit()
