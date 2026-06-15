# features/images/router.py - Endpoints de imágenes con Cloudinary
# GET   /api/v1/images      → Lista todas las imágenes (público)
# GET   /api/v1/images/{id} → Obtiene imagen por ID (público)
# POST  /api/v1/images/upload → Sube imágenes a Cloudinary (requiere ADMIN)
# DELETE /api/v1/images/{id} → Elimina imagen de Cloudinary y DB (requiere ADMIN)

from typing import List
from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlmodel import Session
from app.db.database import get_session
from app.core.uow import UnitOfWork
from app.core.dependencies import require_admin
from app.features.images.schemas import ImagePublic
from app.features.images.service import ImageService
from app.features.images.repository import ImageRepository

router = APIRouter(prefix="/api/v1/images", tags=["Images"])


@router.get("", response_model=List[ImagePublic])
def list_images(session: Session = Depends(get_session)):
    """GET /api/v1/images - Lista todas las imágenes (público)."""
    with UnitOfWork(session) as uow:
        repo = ImageRepository()
        service = ImageService(uow, repo)
        return service.list_all()


@router.get("/{image_id}", response_model=ImagePublic)
def get_image(image_id: int, session: Session = Depends(get_session)):
    """GET /api/v1/images/{id} - Obtiene una imagen por ID (público)."""
    with UnitOfWork(session) as uow:
        repo = ImageRepository()
        service = ImageService(uow, repo)
        return service.get_by_id(image_id)


@router.post("/upload", response_model=List[ImagePublic], status_code=status.HTTP_201_CREATED)
async def upload_images(
    files: List[UploadFile] = File(...),
    session: Session = Depends(get_session),
    _=Depends(require_admin),
):
    """POST /api/v1/images/upload - Sube imágenes a Cloudinary.
    Requiere: rol ADMIN.
    Acepta múltiples archivos (hasta 10 MB c/u, formatos: jpeg, png, gif, webp)."""
    with UnitOfWork(session) as uow:
        repo = ImageRepository()
        service = ImageService(uow, repo)
        return await service.upload_many(files)


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(
    image_id: int,
    session: Session = Depends(get_session),
    _=Depends(require_admin),
):
    """DELETE /api/v1/images/{id} - Elimina imagen de Cloudinary y DB.
    Requiere: rol ADMIN."""
    with UnitOfWork(session) as uow:
        repo = ImageRepository()
        service = ImageService(uow, repo)
        return service.delete(image_id)
