# features/images/service.py - Servicio de imágenes con Cloudinary
# Sigue el patrón del proyecto: recibe UnitOfWork + Repository en el constructor.
# La config de Cloudinary se carga desde app.core.config (NO de un objeto settings).
# NO usa ImageUnitOfWork — usa el UnitOfWork compartido de app/core/uow.py.

import asyncio
import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile, status

from app.core.config import (
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
)
from app.core.uow import UnitOfWork
from app.features.images.models import Image
from app.features.images.repository import ImageRepository

# ── Config global de Cloudinary ──────────────────────────────────────────────
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True,
)

# ── Constantes de validación ─────────────────────────────────────────────────
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


class ImageService:
    """Servicio de imágenes. Delega en ImageRepository para todas las consultas.
    Sigue el patrón del proyecto: UnitOfWork + Repository en el constructor."""

    def __init__(self, uow: UnitOfWork, repo: ImageRepository):
        self.uow = uow
        self.repo = repo

    def list_all(self) -> list[Image]:
        """Lista todas las imágenes ordenadas por fecha descendente."""
        return self.repo.get_all_ordered(self.uow.session)

    def get_by_id(self, image_id: int) -> Image:
        """Obtiene una imagen por ID. Lanza 404 si no existe."""
        image = self.repo.get_by_id(self.uow.session, image_id)
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Imagen no encontrada",
            )
        return image

    async def upload_many(self, files: list[UploadFile]) -> list[Image]:
        """Sube múltiples archivos a Cloudinary y guarda los registros en DB.
        1. Valida tipo y tamaño de cada archivo
        2. Sube a Cloudinary (en hilo separado para no bloquear)
        3. Crea registros Image en DB
        4. Retorna la lista de imágenes creadas"""
        results: list[Image] = []

        for file in files:
            # ── Validar tipo MIME ────────────────────────────────────────────
            if file.content_type not in ALLOWED_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"El archivo '{file.filename}' tiene un tipo no soportado: '{file.content_type}'",
                )

            # ── Leer contenido y validar tamaño ──────────────────────────────
            content = await file.read()
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"El archivo '{file.filename}' supera el límite de 10 MB",
                )

            # ── Subir a Cloudinary ───────────────────────────────────────────
            upload_result = await asyncio.to_thread(
                cloudinary.uploader.upload,
                content,
                folder="rost",
                resource_type="image",
            )

            # ── Crear registro en DB ─────────────────────────────────────────
            image = self.repo.create(
                self.uow.session,
                public_id=upload_result["public_id"],
                url=upload_result["secure_url"],
                filename=file.filename or upload_result["public_id"],
                format=upload_result.get("format"),
                width=upload_result.get("width"),
                height=upload_result.get("height"),
                bytes=upload_result.get("bytes"),
            )
            results.append(image)

        return results

    def delete(self, image_id: int) -> None:
        """Elimina una imagen de Cloudinary y de la DB.
        Lanza 404 si la imagen no existe."""
        image = self.repo.get_by_id(self.uow.session, image_id)
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Imagen no encontrada",
            )

        # Eliminar de Cloudinary
        cloudinary.uploader.destroy(image.public_id, resource_type="image")

        # Eliminar de DB
        self.repo.delete(self.uow.session, image)
