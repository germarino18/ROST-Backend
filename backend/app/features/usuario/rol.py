# features/usuario/rol.py - Modelo de la tabla "roles"
# Catálogo de roles del sistema (ADMIN, STOCK, PEDIDOS, CLIENT).
# La PK es el código textual del rol.

from sqlmodel import SQLModel, Field


class Rol(SQLModel, table=True):
    """Catálogo de roles. PK textual (codigo): ADMIN, STOCK, PEDIDOS, CLIENT."""
    __tablename__ = "roles"

    codigo: str = Field(primary_key=True, max_length=20)
    descripcion: str = Field(max_length=100)
