# features/auth/repository.py - AuthRepository
# Consultas específicas de autenticación sobre el modelo Usuario.

from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.features.auth.models import Usuario


class AuthRepository(BaseRepository[Usuario]):
    """Repositorio de autenticación. Hereda BaseRepository y agrega
    métodos específicos para búsqueda por email y verificación de roles."""

    def __init__(self):
        super().__init__(Usuario)

    def get_by_email(self, session: Session, email: str) -> Usuario | None:
        """Busca un usuario por su email."""
        return session.exec(
            select(Usuario).where(Usuario.email == email)
        ).first()
