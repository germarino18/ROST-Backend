# features/auth/schemas.py - Schemas para autenticación
# AuthRegister: datos de registro (email, nombre, password)
# AuthLogin: credenciales de login (email, password)
# AuthUserRead: respuesta con datos del usuario + roles

from datetime import datetime
from typing import Optional
import re
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class AuthRegister(BaseModel):
    email: EmailStr
    nombre: str = Field(min_length=2, max_length=80)
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe contener al menos una mayúscula")
        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe contener al menos un número")
        if not re.search(r"[^a-zA-Z0-9\s]", v):
            raise ValueError("La contraseña debe contener al menos un símbolo (ej: !@#$%^&*)")
        return v


class AuthLogin(BaseModel):
    email: EmailStr
    password: str


class CambiarPasswordRequest(BaseModel):
    password_actual: str
    password_nueva: str = Field(min_length=8)

    @field_validator("password_nueva")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe contener al menos una mayúscula")
        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe contener al menos un número")
        if not re.search(r"[^a-zA-Z0-9\s]", v):
            raise ValueError("La contraseña debe contener al menos un símbolo (ej: !@#$%^&*)")
        return v


class RolRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    codigo: str
    descripcion: str


class AuthUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    email: str
    nombre: str
    activo: bool
    rol: Optional[RolRead] = None
