# features/producto/models.py - Modelos del módulo Productos

from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship, Column, DateTime, func, DECIMAL, Integer, ARRAY, String, CheckConstraint
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from app.features.categoria.models import Categoria
    from app.features.ingrediente.models import Ingrediente
    from app.features.unidad_medida.models import UnidadMedida
    from app.features.pedido.models import DetallePedido


class Producto(SQLModel, table=True):
    """Tabla productos: catálogo con nombre, precio, stock, disponibilidad."""
    __tablename__ = "productos"

    id: Optional[int] = Field(default=None, primary_key=True)
    unidad_venta_id: Optional[int] = Field(
        default=None, foreign_key="unidades_medida.id", nullable=True
    )
    nombre: str = Field(max_length=200, nullable=False)
    descripcion: Optional[str] = Field(default=None, max_length=1000)
    precio_base: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(DECIMAL(10, 2), CheckConstraint("precio_base >= 0")),
    )
    imagenes_url: Optional[List[str]] = Field(
        default=None, sa_column=Column(ARRAY(String))
    )
    stock_cantidad: Optional[int] = Field(
        default=0,
        sa_column=Column(Integer, CheckConstraint("stock_cantidad >= 0")),
    )
    disponible: Optional[bool] = Field(default=True)
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

    unidad_venta: Optional["UnidadMedida"] = Relationship(back_populates="productos")
    productos_categoria: List["ProductoCategoria"] = Relationship(back_populates="producto")
    productos_ingredientes: List["ProductoIngrediente"] = Relationship(back_populates="producto")
    detalles_pedido: List["DetallePedido"] = Relationship(back_populates="producto")


class ProductoCategoria(SQLModel, table=True):
    """Tabla intermedia productos_categorias (M:N)."""
    __tablename__ = "productos_categorias"

    producto_id: Optional[int] = Field(
        default=None, foreign_key="productos.id", primary_key=True
    )
    categoria_id: Optional[int] = Field(
        default=None, foreign_key="categorias.id", primary_key=True
    )
    es_principal: Optional[bool] = Field(default=False)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    producto: "Producto" = Relationship(back_populates="productos_categoria")
    categoria: "Categoria" = Relationship(back_populates="productos_categoria")


class ProductoIngrediente(SQLModel, table=True):
    """Tabla intermedia productos_ingredientes (M:N)."""
    __tablename__ = "productos_ingredientes"

    producto_id: Optional[int] = Field(
        default=None, foreign_key="productos.id", primary_key=True
    )
    ingrediente_id: Optional[int] = Field(
        default=None, foreign_key="ingredientes.id", primary_key=True
    )
    cantidad: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(DECIMAL(10, 3), CheckConstraint("cantidad > 0")),
    )
    unidad_medida_id: int = Field(foreign_key="unidades_medida.id", nullable=False)
    es_removible: Optional[bool] = Field(default=False)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    producto: "Producto" = Relationship(back_populates="productos_ingredientes")
    ingrediente: "Ingrediente" = Relationship(back_populates="productos_ingredientes")
    unidad_medida: "UnidadMedida" = Relationship(back_populates="productos_ingredientes")
