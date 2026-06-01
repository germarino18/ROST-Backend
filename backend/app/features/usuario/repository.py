# features/usuario/repository.py - UsuarioRepository
# Consultas para administración de usuarios: listado paginado, búsqueda
# por email, gestión de roles.

from typing import List, Optional
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.features.auth.models import Usuario
from app.features.usuario.usuario_rol import UsuarioRol
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
            stmt = stmt.join(UsuarioRol).join(Rol).where(Rol.codigo == rol)
        return list(session.exec(stmt).all())

    def get_roles_by_user_id(self, session: Session, usuario_id: int) -> List[UsuarioRol]:
        """Obtiene todos los roles asignados a un usuario."""
        return list(
            session.exec(
                select(UsuarioRol).where(UsuarioRol.usuario_id == usuario_id)
            ).all()
        )

    def get_user_role_by_codes(
        self, session: Session, usuario_id: int, rol_codigo: str
    ) -> Optional[UsuarioRol]:
        """Obtiene un rol específico de un usuario, o None si no lo tiene."""
        return session.exec(
            select(UsuarioRol).where(
                UsuarioRol.usuario_id == usuario_id,
                UsuarioRol.rol_codigo == rol_codigo,
            )
        ).first()

    def assign_role(self, session: Session, usuario_id: int, rol_codigo: str) -> UsuarioRol:
        """Asigna un rol a un usuario."""
        ur = UsuarioRol(usuario_id=usuario_id, rol_codigo=rol_codigo)
        session.add(ur)
        session.flush()
        return ur

    def remove_role(self, session: Session, ur: UsuarioRol) -> None:
        """Remueve un rol de un usuario."""
        session.delete(ur)
        session.flush()

    def get_rol_by_codigo(self, session: Session, codigo: str) -> Optional[Rol]:
        """Obtiene un rol por su código."""
        return session.exec(select(Rol).where(Rol.codigo == codigo)).first()

    def get_all_roles(self, session: Session) -> List[Rol]:
        """Lista todos los roles del sistema."""
        return list(session.exec(select(Rol)).all())
