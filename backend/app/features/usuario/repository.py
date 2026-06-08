# features/usuario/repository.py - UsuarioRepository
# Consultas para administración de usuarios: listado paginado, búsqueda
# por email, gestión de roles.

from typing import List, Optional
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.features.auth.models import Usuario
from app.features.usuario.rol import Rol


class UsuarioRepository(BaseRepository[Usuario]):
    """Repositorio de usuarios para administración."""

    def __init__(self):
        super().__init__(Usuario)

    def get_all_paginated(
        self,
        session: Session,
        rol: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Usuario]:
        """Lista usuarios activos (sin soft delete) con paginación y filtro opcional por rol."""
        stmt = (
            select(Usuario)
            .where(Usuario.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        if rol:
            stmt = stmt.where(Usuario.rol_codigo == rol)
        return list(session.exec(stmt).all())

    def get_rol_by_codigo(self, session: Session, codigo: str) -> Optional[Rol]:
        """Obtiene un rol por su código."""
        return session.exec(select(Rol).where(Rol.codigo == codigo)).first()

    def get_all_roles(self, session: Session) -> List[Rol]:
        """Lista todos los roles del sistema."""
        return list(session.exec(select(Rol)).all())
