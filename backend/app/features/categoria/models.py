# features/categoria/models.py - Modelo de la tabla "categorias"
# Categorías jerárquicas (parent_id se referencia a sí misma).
# Soporta soft delete y se relaciona con productos vía tabla intermedia.

from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, Column, DateTime, func
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from app.features.producto.models import ProductoCategoria


class Categoria(SQLModel, table=True):
    """Tabla categorias: jerarquía auto-referenciada (parent_id → categorias.id).
    Soft delete. Relación M:N con productos vía tabla intermedia."""
    __tablename__ = "categorias"

    id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: Optional[int] = Field(
        default=None, foreign_key="categorias.id", nullable=True
    )
    nombre: str = Field(max_length=100, unique=True, nullable=False)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    imagen_url: Optional[str] = Field(default=None, max_length=500)
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

    parent: Optional["Categoria"] = Relationship(
        back_populates="hijos",
        sa_relationship_kwargs={"remote_side": "Categoria.id"},
    )
    hijos: List["Categoria"] = Relationship(back_populates="parent")

    productos_categoria: List["ProductoCategoria"] = Relationship(
        back_populates="categoria"
    )
