# features/pagos/schemas.py - Schemas para el módulo de pagos

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CrearPreferenceRequest(BaseModel):
    """Request para crear una preferencia de pago."""
    pedido_id: int


class PagoRead(BaseModel):
    """Respuesta con datos del pago."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    pedido_id: int
    mp_preference_id: Optional[str] = None
    mp_status: str
    mp_status_detail: Optional[str] = None
    transaction_amount: Optional[Decimal] = None
    payment_method_id: Optional[str] = None
    external_reference: Optional[str] = None
    created_at: Optional[datetime] = None


class CrearPreferenceResponse(BaseModel):
    """Respuesta con la preferencia creada en MercadoPago."""
    preference_id: str
    init_point: str


class WebhookPayload(BaseModel):
    """Payload del webhook de MercadoPago."""
    type: str
    data: dict
