# features/images/schemas.py - Schemas del módulo de imágenes
# ImagePublic: respuesta de solo lectura con datos de Cloudinary
# Sigue el patrón de los schemas del proyecto (ConfigDict(from_attributes=True))

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ImagePublic(BaseModel):
    """Schema de respuesta para una imagen subida a Cloudinary.
    Se construye desde el modelo Image (from_attributes=True)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    public_id: str
    url: str
    filename: str
    format: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    bytes: Optional[int] = None
    created_at: datetime
