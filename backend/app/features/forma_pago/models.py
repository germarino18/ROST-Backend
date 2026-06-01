# features/forma_pago/models.py - Modelo de la tabla "formas_pago"
# Catálogo simple de formas de pago.

from sqlmodel import SQLModel, Field
from typing import Optional


class FormaPago(SQLModel, table=True):
    """Catálogo de formas de pago."""
    __tablename__ = "formas_pago"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100, nullable=False, unique=True)
