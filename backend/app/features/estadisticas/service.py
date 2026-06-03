from collections import defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlmodel import Session, select, func, text
from app.features.estadisticas.schemas import DashboardRead, ProductoTop, StockBajo, PedidoDiario


class EstadisticasService:
    """Servicio que construye el dashboard con métricas agregadas del negocio."""

    def __init__(self, session: Session):
        self.session = session

    def get_dashboard(self) -> DashboardRead:
        """Compila todas las métricas del dashboard en una sola respuesta."""
        ahora = datetime.now(timezone.utc)
        hoy_inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
        semana_inicio = hoy_inicio - timedelta(days=7)

        # Pedidos e ingresos de hoy
        from app.features.pedido.models import Pedido

        pedidos_hoy = self.session.exec(
            select(Pedido).where(Pedido.created_at >= hoy_inicio)
        ).all()
        ingresos_hoy = sum(
            float(p.total) for p in pedidos_hoy if p.total and p.estado_actual in ("ENTREGADO", "LISTO")
        )
        # Pedidos e ingresos de la semana
        pedidos_semana = self.session.exec(
            select(Pedido).where(Pedido.created_at >= semana_inicio)
        ).all()
        ingresos_semana = sum(
            float(p.total) for p in pedidos_semana if p.total and p.estado_actual in ("ENTREGADO", "LISTO")
        )

        # Pedidos por estado
        stmt_estados = select(Pedido.estado_actual, func.count(Pedido.id).label("count"))
        stmt_estados = stmt_estados.group_by(Pedido.estado_actual)
        rows_estados = self.session.exec(stmt_estados).all()
        pedidos_por_estado = {row[0]: row[1] for row in rows_estados}

        # Productos más vendidos (top 5)
        from app.features.pedido.models import DetallePedido

        stmt_top = select(
            DetallePedido.nombre_snapshot,
            func.sum(DetallePedido.cantidad).label("total_vendido"),
        )
        stmt_top = stmt_top.group_by(DetallePedido.nombre_snapshot)
        stmt_top = stmt_top.order_by(text("total_vendido DESC"))
        stmt_top = stmt_top.limit(5)
        rows_top = self.session.exec(stmt_top).all()
        productos_mas_vendidos = [
            ProductoTop(nombre=row[0], cantidad=int(row[1])) for row in rows_top if row[0]
        ]

        # Stock bajo (<= 5)
        from app.features.producto.models import Producto

        stmt_stock = select(Producto).where(Producto.stock_cantidad <= 5).where(Producto.disponible == True)
        stock_bajo_rows = self.session.exec(stmt_stock).all()
        stock_bajo = [
            StockBajo(nombre=p.nombre, stock=p.stock_cantidad or 0)
            for p in stock_bajo_rows
        ]

        # Pedidos últimos 7 días (serie temporal)
        pedidos_7_dias = self.session.exec(
            select(Pedido).where(Pedido.created_at >= semana_inicio)
        ).all()
        conteo_dias: dict[str, int] = defaultdict(int)
        for p in pedidos_7_dias:
            dia = p.created_at.strftime("%Y-%m-%d") if p.created_at else "sin-fecha"
            conteo_dias[dia] += 1
        pedidos_ultimos_7_dias = [
            PedidoDiario(fecha=fecha, total=total)
            for fecha, total in sorted(conteo_dias.items())
        ]

        return DashboardRead(
            pedidos_hoy=len(pedidos_hoy),
            ingresos_hoy=ingresos_hoy,
            pedidos_semana=len(pedidos_semana),
            ingresos_semana=ingresos_semana,
            pedidos_por_estado=pedidos_por_estado,
            productos_mas_vendidos=productos_mas_vendidos,
            stock_bajo=stock_bajo,
            pedidos_ultimos_7_dias=pedidos_ultimos_7_dias,
        )
