# features/usuario/usuario_rol.py - Modelo de la tabla "usuarios_roles"
# Tabla intermedia que relaciona usuarios con roles (relación M:N).
# PK compuesta: usuario_id + rol_codigo.

from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, Column, DateTime, func
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.features.auth.models import Usuario
    from app.features.usuario.rol import Rol


class UsuarioRol(SQLModel, table=True):
    """Tabla intermedia usuarios_roles (M:N). PK compuesta: usuario_id + rol_codigo."""
    __tablename__ = "usuarios_roles"

    usuario_id: Optional[int] = Field(
        default=None, foreign_key="usuarios.id", primary_key=True
    )
    rol_codigo: Optional[str] = Field(
        default=None, foreign_key="roles.codigo", primary_key=True, max_length=20
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    usuario: "Usuario" = Relationship(back_populates="roles")
    rol: "Rol" = Relationship()
