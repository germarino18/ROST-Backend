# features/usuario/schemas.py - Schemas para administración de usuarios
# AdminUserUpdate: campos editables de usuario
# AdminUserRead: respuesta con datos + roles
# AdminRolAsignar: body para asignar rol

from datetime import datetime
from typing import List, Optional
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
    roles: List[str] = []


class AdminRolAsignar(BaseModel):
    rol_codigo: str
