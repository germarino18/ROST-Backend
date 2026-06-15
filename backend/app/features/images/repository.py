# features/images/repository.py - ImageRepository
# Hereda de BaseRepository siguiendo el patrón del proyecto:
# - __init__ solo guarda el modelo (no la session)
# - La session se pasa como argumento a cada método

from typing import Optional
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.features.images.models import Image


class ImageRepository(BaseRepository[Image]):
    """Repositorio de imágenes con consultas específicas."""

    def __init__(self):
        super().__init__(Image)

    def get_all_ordered(self, session: Session) -> list[Image]:
        """Lista todas las imágenes ordenadas por fecha de creación descendente."""
        return list(
            session.exec(
                select(Image).order_by(Image.created_at.desc())
            ).all()
        )

    def get_by_public_id(self, session: Session, public_id: str) -> Optional[Image]:
        """Busca una imagen por su public_id de Cloudinary."""
        return session.exec(
            select(Image).where(Image.public_id == public_id)
        ).first()

    def get_by_url(self, session: Session, url: str) -> Optional[Image]:
        """Busca una imagen por su URL."""
        return session.exec(
            select(Image).where(Image.url == url)
        ).first()
