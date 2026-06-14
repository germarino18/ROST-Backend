# features/pedido/repository.py - PedidoRepository
# Consultas para pedidos con eager loading de detalles e historial.

from typing import List, Optional
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.core.repository import BaseRepository
from app.features.pedido.models import (
    Pedido,
    DetallePedido,
    HistorialEstadoPedido,
    EstadoPedido,
)
from app.features.producto.models import Producto


_pedido_loads = (
    selectinload(Pedido.detalles),
    selectinload(Pedido.historial),
    selectinload(Pedido.usuario),
)


class PedidoRepository(BaseRepository[Pedido]):
    """Repositorio de pedidos con eager loading de detalles e historial."""

    def __init__(self):
        super().__init__(Pedido)

    def get_all(self, session: Session, usuario_id: Optional[int] = None) -> List[Pedido]:
        """Lista pedidos. Si usuario_id está presente, filtra por ese usuario.
        Ordena por created_at descendente."""
        stmt = select(Pedido).options(*_pedido_loads)
        if usuario_id is not None:
            stmt = stmt.where(Pedido.usuario_id == usuario_id)
        stmt = stmt.order_by(Pedido.created_at.desc())
        return list(session.exec(stmt).all())

    def get_by_id_with_relations(self, session: Session, id: int) -> Optional[Pedido]:
        """Obtiene pedido por ID con detalles e historial precargados."""
        return session.exec(
            select(Pedido).where(Pedido.id == id).options(*_pedido_loads)
        ).first()

    def get_producto(self, session: Session, producto_id: int) -> Optional[Producto]:
        """Obtiene un producto por ID."""
        return session.get(Producto, producto_id)

    def create_detalle(self, session: Session, **data) -> DetallePedido:
        """Crea un detalle de pedido."""
        detalle = DetallePedido(**data)
        session.add(detalle)
        return detalle

    def create_historial(
        self, session: Session, pedido_id: int, estado: str, cambiado_por: int
    ) -> HistorialEstadoPedido:
        """Registra un cambio de estado en el historial."""
        historial = HistorialEstadoPedido(
            pedido_id=pedido_id,
            estado=estado,
            cambiado_por=cambiado_por,
        )
        session.add(historial)
        return historial

    def get_forma_pago(self, session: Session, forma_pago_id: int):
        """Obtiene una forma de pago por ID."""
        from app.features.forma_pago.models import FormaPago
        return session.get(FormaPago, forma_pago_id)

    def update_producto_stock(
        self, session: Session, producto: Producto, cantidad: int
    ) -> None:
        """Descuenta stock de un producto."""
        if producto.stock_cantidad is not None:
            producto.stock_cantidad -= cantidad
            session.add(producto)
