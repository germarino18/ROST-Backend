# features/pedido/models.py - Modelos del módulo Pedidos

from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship, Column, DateTime, func, DECIMAL, JSON, CheckConstraint
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from app.features.pagos.models import Pago

if TYPE_CHECKING:
    from app.features.auth.models import Usuario
    from app.features.direccion.models import DireccionEntrega
    from app.features.forma_pago.models import FormaPago
    from app.features.producto.models import Producto


class EstadoPedido(SQLModel, table=True):
    """Catálogo de estados de pedido."""
    __tablename__ = "estados_pedido"
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(max_length=20, nullable=False, unique=True)


class Pedido(SQLModel, table=True):
    """Tabla pedidos: cabecera del pedido."""
    __tablename__ = "pedidos"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuarios.id", nullable=False)
    direccion_entrega_id: Optional[int] = Field(
        default=None, foreign_key="direcciones_entrega.id", nullable=True
    )
    forma_pago_id: Optional[int] = Field(
        default=None, foreign_key="formas_pago.id", nullable=True
    )
    estado_actual: str = Field(max_length=20, nullable=False)
    total: Optional[Decimal] = Field(
        default=None, sa_column=Column(DECIMAL(12, 2))
    )
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

    usuario: "Usuario" = Relationship(back_populates="pedidos")
    direccion_entrega: "DireccionEntrega" = Relationship()
    forma_pago: "FormaPago" = Relationship()
    detalles: List["DetallePedido"] = Relationship(back_populates="pedido")
    historial: List["HistorialEstadoPedido"] = Relationship(back_populates="pedido")
    pago: Optional["Pago"] = Relationship(back_populates="pedido")


class DetallePedido(SQLModel, table=True):
    """Líneas de pedido con snapshot de precio y nombre."""
    __tablename__ = "detalles_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id", nullable=False)
    producto_id: int = Field(foreign_key="productos.id", nullable=False)
    cantidad: int = Field(nullable=False)
    precio_snapshot: Optional[Decimal] = Field(
        default=None, sa_column=Column(DECIMAL(10, 2))
    )
    nombre_snapshot: str = Field(max_length=200, nullable=False)
    personalizacion: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    pedido: "Pedido" = Relationship(back_populates="detalles")
    producto: "Producto" = Relationship(back_populates="detalles_pedido")


class HistorialEstadoPedido(SQLModel, table=True):
    """Registro append-only de cambios de estado de un pedido."""
    __tablename__ = "historial_estados_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id", nullable=False)
    estado: str = Field(max_length=20, nullable=False)
    cambiado_por: int = Field(nullable=False)
    fecha: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    pedido: "Pedido" = Relationship(back_populates="historial")
