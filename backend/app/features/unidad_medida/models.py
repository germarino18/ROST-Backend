# features/unidad_medida/models.py - Modelo de la tabla "unidades_medida"
# Catálogo de unidades de medida (kg, g, L, mL, unidades, etc.)

from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, Column, DateTime, func
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from app.features.producto.models import Producto, ProductoIngrediente


class UnidadMedida(SQLModel, table=True):
    """Catálogo de unidades de medida (kg, g, L, mL, u, doc, m²)."""
    __tablename__ = "unidades_medida"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=50, unique=True, nullable=False)
    simbolo: str = Field(max_length=10, unique=True, nullable=False)
    tipo: str = Field(max_length=20, nullable=False)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    productos: List["Producto"] = Relationship(back_populates="unidad_venta")
    productos_ingredientes: List["ProductoIngrediente"] = Relationship(
        back_populates="unidad_medida"
    )
