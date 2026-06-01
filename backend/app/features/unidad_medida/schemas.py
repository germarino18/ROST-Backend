# features/unidad_medida/schemas.py - Schemas para unidades de medida
# UnidadMedidaCreate: creación con nombre, símbolo, tipo
# UnidadMedidaUpdate: actualización parcial
# UnidadMedidaRead: respuesta de la unidad

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class UnidadMedidaCreate(BaseModel):
    nombre: str
    simbolo: str
    tipo: str


class UnidadMedidaUpdate(BaseModel):
    nombre: Optional[str] = None
    simbolo: Optional[str] = None
    tipo: Optional[str] = None


class UnidadMedidaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    simbolo: str
    tipo: str
    created_at: Optional[datetime] = None
