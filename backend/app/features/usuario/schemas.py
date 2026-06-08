# features/usuario/schemas.py - Schemas para administración de usuarios
# AdminUserUpdate: campos editables de usuario
# AdminUserRead: respuesta con datos + rol_codigo
# AdminUserCreate: body para crear usuario con rol único

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AdminUserUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
    activo: Optional[bool] = None


class AdminUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    nombre: str
    activo: bool
    created_at: Optional[datetime] = None
    rol_codigo: Optional[str] = None


class AdminUserCreate(BaseModel):
    email: str
    nombre: str
    password: str
    rol_codigo: str
