# features/direccion/service.py - Servicio de direcciones de entrega
# CRUD scoped por usuario. NO contiene consultas ORM directas.

from typing import List
from fastapi import HTTPException
from app.core.uow import UnitOfWork
from app.features.direccion.models import DireccionEntrega
from app.features.direccion.schemas import DireccionCreate, DireccionUpdate
from app.features.direccion.repository import DireccionRepository


class DireccionService:
    """Servicio de direcciones de entrega. CRUD scoped por usuario."""

    def __init__(self, uow: UnitOfWork, repo: DireccionRepository):
        self.uow = uow
        self.repo = repo

    def get_all(self, usuario_id: int) -> List[DireccionEntrega]:
        return self.repo.get_all_by_usuario(self.uow.session, usuario_id)

    def get_by_id(self, id: int, usuario_id: int) -> DireccionEntrega:
        direccion = self.repo.get_by_id_and_usuario(
            self.uow.session, id, usuario_id
        )
        if not direccion:
            raise HTTPException(status_code=404, detail="Dirección no encontrada")
        return direccion

    def create(self, data: DireccionCreate, usuario_id: int) -> DireccionEntrega:
        direccion = self.repo.create(
            self.uow.session, **data.model_dump(), usuario_id=usuario_id
        )
        self.uow.commit()
        return direccion

    def update(
        self, id: int, data: DireccionUpdate, usuario_id: int
    ) -> DireccionEntrega:
        session = self.uow.session
        direccion = self.get_by_id(id, usuario_id)
        update_data = data.model_dump(exclude_unset=True)
        if update_data:
            direccion = self.repo.update(session, direccion, **update_data)
        self.uow.commit()
        return direccion

    def delete(self, id: int, usuario_id: int) -> None:
        direccion = self.get_by_id(id, usuario_id)
        self.repo.soft_delete(self.uow.session, direccion)
        self.uow.commit()

    def set_principal(self, id: int, usuario_id: int) -> DireccionEntrega:
        session = self.uow.session
        self.repo.unset_all_principal(session, usuario_id)
        direccion = self.get_by_id(id, usuario_id)
        direccion.es_principal = True
        session.add(direccion)
        session.flush()
        session.refresh(direccion)
        self.uow.commit()
        return direccion
