# features/usuario/service.py - Servicio de administración de usuarios
# Toda la lógica de negocio para gestión de usuarios y roles.
# NO contiene consultas ORM directas — delega en UsuarioRepository.

from typing import List, Optional
from fastapi import HTTPException, status
from app.core.uow import UnitOfWork
from app.core.security import hash_password
from app.features.auth.models import Usuario
from app.features.usuario.schemas import AdminUserCreate, AdminUserRead, AdminUserUpdate
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
        return [
            AdminUserRead(
                id=user.id,
                email=user.email,
                nombre=user.nombre,
                activo=user.activo,
                created_at=user.created_at,
                rol_codigo=user.rol_codigo,
            )
            for user in users
        ]

    def actualizar_usuario(self, id: int, data: AdminUserUpdate) -> AdminUserRead:
        """Actualiza datos de un usuario (nombre, email, activo)."""
        session = self.uow.session
        user = self.repo.get_by_id_or_404(session, id)
        if user.deleted_at is not None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        update_data = data.model_dump(exclude_unset=True)
        if update_data:
            user = self.repo.update(session, user, **update_data)

        return AdminUserRead(
            id=user.id,
            email=user.email,
            nombre=user.nombre,
            activo=user.activo,
            created_at=user.created_at,
            rol_codigo=user.rol_codigo,
        )

    def crear_usuario(self, data: AdminUserCreate) -> AdminUserRead:
        """Crea un usuario con un rol específico (solo ADMIN).
        NO asigna CLIENT automáticamente — el ADMIN decide qué rol dar."""
        session = self.uow.session

        existing = self.repo.get_by_email(session, data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El email ya está registrado",
            )

        rol = self.repo.get_rol_by_codigo(session, data.rol_codigo)
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"El rol '{data.rol_codigo}' no existe en el sistema",
            )

        user = Usuario(
            email=data.email,
            nombre=data.nombre,
            password_hash=hash_password(data.password),
            rol_codigo=data.rol_codigo,
        )
        session.add(user)
        session.flush()
        session.refresh(user)
        return AdminUserRead(
            id=user.id,
            email=user.email,
            nombre=user.nombre,
            activo=user.activo,
            created_at=user.created_at,
            rol_codigo=user.rol_codigo,
        )
