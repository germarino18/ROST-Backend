from sqlmodel import Session, select, func, text
from datetime import datetime
from app.features.pedido.models import Pedido, DetallePedido
from app.features.producto.models import Producto


class EstadisticasRepository:

    def get_pedidos_desde(self, session: Session, desde: datetime) -> list[Pedido]:
        """Pedidos creados desde una fecha."""
        return session.exec(select(Pedido).where(Pedido.created_at >= desde)).all()

    def get_pedidos_por_estado(self, session: Session):
        """Conteo de pedidos agrupados por estado."""
        stmt = select(Pedido.estado_actual, func.count(Pedido.id).label("count")).group_by(Pedido.estado_actual)
        return session.exec(stmt).all()

    def get_productos_mas_vendidos(self, session: Session, limit: int = 5):
        """Top N productos por cantidad vendida."""
        stmt = (
            select(DetallePedido.nombre_snapshot, func.sum(DetallePedido.cantidad).label("total_vendido"))
            .group_by(DetallePedido.nombre_snapshot)
            .order_by(text("total_vendido DESC"))
            .limit(limit)
        )
        return session.exec(stmt).all()

    def get_productos_stock_bajo(self, session: Session, umbral: int = 5) -> list[Producto]:
        """Productos con stock menor o igual al umbral y disponibles."""
        return session.exec(
            select(Producto).where(Producto.stock_cantidad <= umbral).where(Producto.disponible == True)
        ).all()
