# features/usuario/service.py - Servicio de administración de usuarios
# Toda la lógica de negocio para gestión de usuarios y roles.
# NO contiene consultas ORM directas — delega en UsuarioRepository.

from typing import List, Optional
from fastapi import HTTPException
from app.core.uow import UnitOfWork
from app.features.auth.models import Usuario
from app.features.usuario.schemas import AdminUserRead, AdminUserUpdate, AdminRolAsignar
from app.features.usuario.repository import UsuarioRepository


class AdminService:
    """Servicio de administración de usuarios y roles."""

    def __init__(self, uow: UnitOfWork, repo: UsuarioRepository):
        self.uow = uow
        self.repo = repo

    def listar_roles(self) -> list:
        """Lista todos los roles del sistema."""
        return self.repo.get_all_roles(self.uow.session)

    def listar_usuarios(
        self,
        rol: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[AdminUserRead]:
        """Lista usuarios activos con paginación y filtro opcional por rol."""
        users = self.repo.get_all_paginated(
            self.uow.session, rol=rol, skip=skip, limit=limit
        )
        result = []
        for user in users:
            user_roles = self.repo.get_roles_by_user_id(self.uow.session, user.id)
            result.append(AdminUserRead(
                id=user.id,
                email=user.email,
                nombre=user.nombre,
                activo=user.activo,
                created_at=user.created_at,
                roles=[ur.rol_codigo for ur in user_roles],
            ))
        return result

    def actualizar_usuario(self, id: int, data: AdminUserUpdate) -> AdminUserRead:
        """Actualiza datos de un usuario (nombre, email, activo)."""
        session = self.uow.session
        user = self.repo.get_by_id_or_404(session, id)
        if user.deleted_at is not None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        update_data = data.model_dump(exclude_unset=True)
        if update_data:
            user = self.repo.update(session, user, **update_data)
            self.uow.commit()

        user_roles = self.repo.get_roles_by_user_id(session, user.id)
        return AdminUserRead(
            id=user.id,
            email=user.email,
            nombre=user.nombre,
            activo=user.activo,
            created_at=user.created_at,
            roles=[ur.rol_codigo for ur in user_roles],
        )

    def asignar_rol(self, usuario_id: int, rol_codigo: str) -> dict:
        """Asigna un rol a un usuario."""
        session = self.uow.session
        user = self.repo.get_by_id_or_404(session, usuario_id)
        if user.deleted_at is not None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        rol = self.repo.get_rol_by_codigo(session, rol_codigo)
        if not rol:
            raise HTTPException(status_code=404, detail="Rol no encontrado")

        existing = self.repo.get_user_role_by_codes(session, usuario_id, rol_codigo)
        if not existing:
            self.repo.assign_role(session, usuario_id, rol_codigo)
            self.uow.commit()

        return {"message": f"Rol {rol_codigo} asignado al usuario {usuario_id}"}

    def remover_rol(self, usuario_id: int, rol_codigo: str) -> dict:
        """Remueve un rol de un usuario."""
        session = self.uow.session
        ur = self.repo.get_user_role_by_codes(session, usuario_id, rol_codigo)
        if not ur:
            raise HTTPException(
                status_code=404,
                detail="El usuario no tiene ese rol",
            )
        self.repo.remove_role(session, ur)
        self.uow.commit()
        return {"message": f"Rol {rol_codigo} removido del usuario {usuario_id}"}
