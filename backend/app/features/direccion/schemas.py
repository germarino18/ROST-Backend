# features/direccion/schemas.py - Schemas para direcciones de entrega
# DireccionCreate: creación con alias, dirección, ciudad, región
# DireccionUpdate: actualización parcial
# DireccionRead: respuesta con datos + flag es_principal

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class DireccionCreate(BaseModel):
    alias: str
    direccion: str
    ciudad: str
    region: str
    codigo_postal: Optional[str] = None


class DireccionUpdate(BaseModel):
    alias: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    region: Optional[str] = None
    codigo_postal: Optional[str] = None


class DireccionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    alias: str
    direccion: str
    ciudad: str
    region: str
    codigo_postal: Optional[str] = None
    es_principal: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
