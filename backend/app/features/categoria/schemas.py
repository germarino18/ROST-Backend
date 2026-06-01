# features/categoria/schemas.py - Schemas para categorías
# CategoriaCreate: creación con nombre, descripción, parent_id, imagen
# CategoriaUpdate: actualización parcial
# CategoriaRead: respuesta con subcategorías (hijos)

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class CategoriaCreate(BaseModel):
    parent_id: Optional[int] = None
    nombre: str
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None


class CategoriaUpdate(BaseModel):
    parent_id: Optional[int] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None


class CategoriaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    parent_id: Optional[int] = None
    nombre: str
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    hijos: Optional[List["CategoriaRead"]] = None
