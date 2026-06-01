# features/auth/schemas.py - Schemas para autenticación
# AuthRegister: datos de registro (email, nombre, password)
# AuthLogin: credenciales de login (email, password)
# AuthUserRead: respuesta con datos del usuario + roles

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AuthRegister(BaseModel):
    email: str
    nombre: str
    password: str


class AuthLogin(BaseModel):
    email: str
    password: str


class RolRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    codigo: str
    descripcion: str


class UsuarioRolRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    rol_codigo: str
    rol: Optional[RolRead] = None


class AuthUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    email: str
    nombre: str
    activo: bool
    roles: list[UsuarioRolRead] = []
