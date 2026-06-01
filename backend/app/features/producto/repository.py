# features/producto/repository.py - ProductoRepository
# Consultas específicas: búsqueda textual, filtro por categoría/disponibilidad,
# eager loading de relaciones M:N, gestión de categorías e ingredientes.

from datetime import datetime, timezone
from typing import List, Optional
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.core.repository import BaseRepository
from app.features.producto.models import (
    Producto,
    ProductoCategoria,
    ProductoIngrediente,
)


# Opciones de eager loading reutilizables para producto
_producto_loads = (
    selectinload(Producto.productos_categoria).selectinload(ProductoCategoria.categoria),
    selectinload(Producto.productos_ingredientes).selectinload(ProductoIngrediente.ingrediente),
    selectinload(Producto.productos_ingredientes).selectinload(ProductoIngrediente.unidad_medida),
    selectinload(Producto.unidad_venta),
)


class ProductoRepository(BaseRepository[Producto]):
    """Repositorio de productos con eager loading y gestión de relaciones M:N."""

    def __init__(self):
        super().__init__(Producto)

    def get_all_filtered(
        self,
        session: Session,
        q: Optional[str] = None,
        categoria_id: Optional[int] = None,
        disponible: Optional[bool] = None,
    ) -> List[Producto]:
        """Lista productos activos con filtros opcionales y relaciones precargadas."""
        stmt = (
            select(Producto)
            .where(Producto.deleted_at.is_(None))
            .options(*_producto_loads)
        )
        if q:
            stmt = stmt.where(Producto.nombre.ilike(f"%{q}%"))
        if disponible is not None:
            stmt = stmt.where(Producto.disponible == disponible)
        if categoria_id is not None:
            stmt = stmt.join(ProductoCategoria).where(
                ProductoCategoria.categoria_id == categoria_id
            )
        return list(session.exec(stmt).all())

    def get_by_id_with_relations(self, session: Session, id: int) -> Optional[Producto]:
        """Obtiene producto activo por ID con relaciones precargadas."""
        return session.exec(
            select(Producto)
            .where(Producto.id == id, Producto.deleted_at.is_(None))
            .options(*_producto_loads)
        ).first()

    def replace_categorias(
        self, session: Session, producto_id: int, categoria_ids: List[int]
    ) -> None:
        """Reemplaza todas las categorías de un producto."""
        existing = session.exec(
            select(ProductoCategoria).where(ProductoCategoria.producto_id == producto_id)
        ).all()
        for pc in existing:
            session.delete(pc)
        for cat_id in categoria_ids:
            session.add(ProductoCategoria(producto_id=producto_id, categoria_id=cat_id))

    def replace_ingredientes(
        self, session: Session, producto_id: int, ingredientes: List[dict]
    ) -> None:
        """Reemplaza todos los ingredientes de un producto."""
        existing = session.exec(
            select(ProductoIngrediente).where(ProductoIngrediente.producto_id == producto_id)
        ).all()
        for pi in existing:
            session.delete(pi)
        for ing_data in ingredientes:
            session.add(
                ProductoIngrediente(
                    producto_id=producto_id,
                    ingrediente_id=ing_data["ingrediente_id"],
                    cantidad=ing_data.get("cantidad"),
                    unidad_medida_id=ing_data["unidad_medida_id"],
                    es_removible=ing_data.get("es_removible", False),
                )
            )

    def soft_delete(self, session: Session, obj: Producto) -> None:
        """Marca deleted_at en lugar de eliminar."""
        obj.deleted_at = datetime.now(timezone.utc)
        session.add(obj)
        session.flush()
