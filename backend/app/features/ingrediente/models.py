# features/ingrediente/models.py - Modelo de la tabla "ingredientes"
# Ingredientes con indicador de alérgeno. Se relaciona con productos
# vía tabla intermedia productos_ingredientes (M:N).

from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, Column, DateTime, func
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from app.features.producto.models import ProductoIngrediente


class Ingrediente(SQLModel, table=True):
    """Tabla ingredientes: nombre único, indicador de alérgeno."""
    __tablename__ = "ingredientes"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100, unique=True, nullable=False)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    es_alergeno: Optional[bool] = Field(default=False)
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

    productos_ingredientes: List["ProductoIngrediente"] = Relationship(
        back_populates="ingrediente"
    )
