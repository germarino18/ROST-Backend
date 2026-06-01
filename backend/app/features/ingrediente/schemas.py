# features/ingrediente/schemas.py - Schemas para ingredientes
# IngredienteCreate: creación con nombre, descripción, es_alergeno
# IngredienteUpdate: actualización parcial
# IngredienteRead: respuesta del ingrediente

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class IngredienteCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    es_alergeno: Optional[bool] = False


class IngredienteUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    es_alergeno: Optional[bool] = None


class IngredienteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: Optional[str] = None
    es_alergeno: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
