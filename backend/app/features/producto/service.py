# features/producto/service.py - Servicio de productos
# Lógica de negocio: filtros, relaciones M:N, soft delete, regla stock=0 → no disponible.
# NO contiene consultas ORM directas — delega en ProductoRepository.

from datetime import datetime, timezone
from typing import List, Optional
import cloudinary.uploader
from fastapi import HTTPException
from sqlmodel import select
from app.core.uow import UnitOfWork
from app.features.producto.models import Producto
from app.features.producto.schemas import ProductoCreate, ProductoUpdate
from app.features.producto.repository import ProductoRepository
from app.features.images.models import Image


class ProductoService:
    """Servicio de productos. Delega en repositorio para todas las consultas."""

    def __init__(self, uow: UnitOfWork, repo: ProductoRepository):
        self.uow = uow
        self.repo = repo

    def get_all(
        self,
        q: Optional[str] = None,
        categoria_id: Optional[int] = None,
        disponible: Optional[bool] = None,
    ) -> List[Producto]:
        return self.repo.get_all_filtered(
            self.uow.session, q=q, categoria_id=categoria_id, disponible=disponible
        )

    def get_by_id(self, id: int) -> Producto:
        obj = self.repo.get_by_id_with_relations(self.uow.session, id)
        if not obj:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return obj

    def create(self, schema: ProductoCreate) -> Producto:
        session = self.uow.session
        data = schema.model_dump(
            exclude={"categorias", "ingredientes"}, exclude_unset=False
        )
        stock = data.get("stock_cantidad", 0)
        if stock is not None and stock == 0:
            data["disponible"] = False
        producto = self.repo.create(session, **data)

        if schema.categorias:
            self.repo.replace_categorias(session, producto.id, schema.categorias)

        if schema.ingredientes:
            self.repo.replace_ingredientes(session, producto.id, schema.ingredientes)

        session.flush()
        session.refresh(producto)
        return producto

    def update(self, id: int, schema: ProductoUpdate) -> Producto:
        session = self.uow.session
        obj = self.get_by_id(id)
        old_urls = set(obj.imagenes_url or [])

        data = schema.model_dump(
            exclude={"categorias", "ingredientes"}, exclude_unset=True
        )
        for key, value in data.items():
            setattr(obj, key, value)

        # Si se cambiaron las URLs de imágenes, limpiar las removidas
        if "imagenes_url" in data:
            new_urls = set(data["imagenes_url"] or [])
            removed = old_urls - new_urls
            if removed:
                self._cleanup_images(list(removed))
        if (
            "stock_cantidad" in data
            and data["stock_cantidad"] is not None
            and data["stock_cantidad"] == 0
        ):
            obj.disponible = False
        obj.updated_at = datetime.now(timezone.utc)
        session.add(obj)
        session.flush()

        if schema.categorias is not None:
            self.repo.replace_categorias(session, id, schema.categorias)

        if schema.ingredientes is not None:
            self.repo.replace_ingredientes(session, id, schema.ingredientes)

        session.flush()
        session.refresh(obj)
        return obj

    def _cleanup_images(self, urls: list[str]) -> None:
        """Elimina imágenes de Cloudinary y de la DB dada una lista de URLs."""
        if not urls:
            return
        session = self.uow.session
        for url in urls:
            image = session.exec(select(Image).where(Image.url == url)).first()
            if image:
                try:
                    cloudinary.uploader.destroy(image.public_id, resource_type="image")
                except Exception:
                    pass  # No bloquear si falla Cloudinary
                session.delete(image)

    def delete(self, id: int) -> None:
        obj = self.get_by_id(id)
        self._cleanup_images(obj.imagenes_url or [])
        self.repo.soft_delete(self.uow.session, obj)

    def cambiar_disponibilidad(self, id: int, disponible: bool) -> Producto:
        session = self.uow.session
        obj = self.get_by_id(id)
        obj.disponible = disponible
        obj.updated_at = datetime.now(timezone.utc)
        session.add(obj)
        session.flush()
        session.refresh(obj)
        return obj
