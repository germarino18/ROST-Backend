# features/pagos/models.py - Modelo de pagos con MercadoPago
# Tabla: pagos. Almacena el estado de cada pago, referencias a MercadoPago,
# clave de idempotencia para evitar cobros duplicados.

from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship, Column, DateTime, DECIMAL, BigInteger, func
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.features.pedido.models import Pedido


class Pago(SQLModel, table=True):
    """Pago de un pedido vía MercadoPago Checkout PRO."""
    __tablename__ = "pagos"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id", nullable=False, unique=True)
    mp_payment_id: Optional[int] = Field(default=None, sa_column=Column(BigInteger, unique=True, nullable=True))
    mp_preference_id: Optional[str] = Field(default=None, nullable=True)
    mp_status: str = Field(default="pending", max_length=20, nullable=False)
    mp_status_detail: Optional[str] = Field(default=None, nullable=True)
    transaction_amount: Optional[Decimal] = Field(
        default=None, sa_column=Column(DECIMAL(10, 2))
    )
    payment_method_id: Optional[str] = Field(default=None, max_length=50, nullable=True)
    external_reference: Optional[str] = Field(default=None, unique=True, nullable=True)
    idempotency_key: str = Field(max_length=36, unique=True, nullable=False)
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

    pedido: "Pedido" = Relationship(back_populates="pago")
