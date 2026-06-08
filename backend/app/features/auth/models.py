# features/auth/models.py - Modelo Usuario para autenticación
# Representa a los usuarios del sistema. Incluye autenticación (email + password_hash),
# soft delete (deleted_at), y rol único FK directa a roles.

from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, Column, DateTime, func
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from app.features.usuario.rol import Rol
    from app.features.direccion.models import DireccionEntrega
    from app.features.pedido.models import Pedido


class Usuario(SQLModel, table=True):
    """Tabla usuarios: almacena cuentas de usuario con email único, nombre,
    password hasheado, estado activo/inactivo y soft delete (deleted_at)."""
    __tablename__ = "usuarios"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=255, unique=True, nullable=False)
    nombre: str = Field(max_length=100, nullable=False)
    password_hash: str = Field(max_length=255, nullable=False)
    activo: bool = Field(default=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        ),
    )
    deleted_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    rol_codigo: Optional[str] = Field(default=None, foreign_key="roles.codigo", max_length=20)
    rol: Optional["Rol"] = Relationship(back_populates="usuarios")
    direcciones: List["DireccionEntrega"] = Relationship(back_populates="usuario")
    pedidos: List["Pedido"] = Relationship(back_populates="usuario")
