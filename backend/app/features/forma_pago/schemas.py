# features/forma_pago/schemas.py - Schemas para formas de pago
# FormaPagoRead: respuesta con id y nombre

from typing import Optional
from pydantic import BaseModel, ConfigDict


class FormaPagoCreate(BaseModel):
    nombre: str


class FormaPagoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
