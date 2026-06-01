# features/direccion/models.py - Modelo de la tabla "direcciones_entrega"
# Direcciones de entrega asociadas a un usuario. Cada usuario puede tener
# múltiples direcciones, con una marcada como principal. Soporta soft delete.

from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, Column, DateTime, func
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.features.auth.models import Usuario


class DireccionEntrega(SQLModel, table=True):
    """Direcciones de entrega por usuario. Cada usuario puede tener varias,
    con una marcada como principal. Soporta soft delete."""
    __tablename__ = "direcciones_entrega"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuarios.id", nullable=False)
    alias: str = Field(max_length=50, nullable=False)
    direccion: str = Field(max_length=255, nullable=False)
    ciudad: str = Field(max_length=100, nullable=False)
    region: str = Field(max_length=100, nullable=False)
    codigo_postal: Optional[str] = Field(default=None, max_length=20)
    es_principal: bool = Field(default=False)
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

    usuario: "Usuario" = Relationship(back_populates="direcciones")
