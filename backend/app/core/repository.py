# core/repository.py - BaseRepository genérico (Patrón Repository)
# Define operaciones CRUD abstractas para cualquier modelo SQLModel.
# Los repositorios concretos heredan de esta clase y agregan métodos específicos.
# Los servicios NUNCA llaman a session.exec() directamente — siempre usan repositorios.

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from fastapi import HTTPException
from sqlmodel import SQLModel, Session, select

ModelT = TypeVar("ModelT", bound=SQLModel)


class BaseRepository(Generic[ModelT]):
    """Repositorio genérico CRUD para cualquier modelo SQLModel.
    Type param: ModelT (modelo SQLModel con table=True).
    Todos los métodos reciben la session explícitamente (no la almacenan)."""

    def __init__(self, model: Type[ModelT]):
        self.model = model

    def get_all(self, session: Session, **filters) -> List[ModelT]:
        """Lista todas las entidades con filtros dinámicos.
        Los valores None se ignoran (no filtran)."""
        stmt = select(self.model)
        for key, value in filters.items():
            if value is not None:
                column = getattr(self.model, key, None)
                if column is not None:
                    stmt = stmt.where(column == value)
        return list(session.exec(stmt).all())

    def get_by_id(self, session: Session, id: int) -> Optional[ModelT]:
        """Obtiene una entidad por su ID. Retorna None si no existe."""
        return session.get(self.model, id)

    def get_by_id_or_404(self, session: Session, id: int) -> ModelT:
        """Obtiene una entidad por su ID. Lanza 404 si no existe."""
        obj = self.get_by_id(session, id)
        if not obj:
            raise HTTPException(
                status_code=404,
                detail=f"{self.model.__name__} no encontrado",
            )
        return obj

    def create(self, session: Session, **data: Any) -> ModelT:
        """Crea una nueva entidad con los datos proporcionados."""
        obj = self.model(**data)
        session.add(obj)
        session.flush()
        session.refresh(obj)
        return obj

    def update(self, session: Session, obj: ModelT, **data: Any) -> ModelT:
        """Actualiza parcialmente una entidad (solo campos enviados)."""
        for key, value in data.items():
            setattr(obj, key, value)
        session.add(obj)
        session.flush()
        session.refresh(obj)
        return obj

    def delete(self, session: Session, obj: ModelT) -> None:
        """Elimina físicamente una entidad."""
        session.delete(obj)
        session.flush()
