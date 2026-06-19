# features/estadisticas/service.py - Servicio de estadísticas del dashboard
# Consultas agregadas sobre tablas existentes: COUNT, SUM, GROUP BY, TOP 5.

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlmodel import Session
from app.features.estadisticas.schemas import DashboardRead, ProductoTop, StockBajo, PedidoDiario
from app.features.estadisticas.repository import EstadisticasRepository


class EstadisticasService:
    """Servicio que construye el dashboard con métricas agregadas del negocio."""

    def __init__(self, session: Session, repo: EstadisticasRepository = None):
        self.session = session
        self.repo = repo or EstadisticasRepository()

    def get_dashboard(self) -> DashboardRead:
        """Compila todas las métricas del dashboard en una sola respuesta."""
        ahora = datetime.now(timezone.utc)
        hoy_inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
        semana_inicio = hoy_inicio - timedelta(days=7)

        # Pedidos e ingresos de hoy
        pedidos_hoy = self.repo.get_pedidos_desde(self.session, hoy_inicio)
        ingresos_hoy = sum(
            float(p.total) for p in pedidos_hoy if p.total and p.estado_actual in ("ENTREGADO", "LISTO")
        )
        # Pedidos e ingresos de la semana
        pedidos_semana = self.repo.get_pedidos_desde(self.session, semana_inicio)
        ingresos_semana = sum(
            float(p.total) for p in pedidos_semana if p.total and p.estado_actual in ("ENTREGADO", "LISTO")
        )

        # Pedidos por estado
        rows_estados = self.repo.get_pedidos_por_estado(self.session)
        pedidos_por_estado = {row[0]: row[1] for row in rows_estados}

        # Productos más vendidos (top 5)
        rows_top = self.repo.get_productos_mas_vendidos(self.session, 5)
        productos_mas_vendidos = [
            ProductoTop(nombre=row[0], cantidad=int(row[1])) for row in rows_top if row[0]
        ]

        # Stock bajo (<= 5)
        stock_bajo_rows = self.repo.get_productos_stock_bajo(self.session, 5)
        stock_bajo = [
            StockBajo(nombre=p.nombre, stock=p.stock_cantidad or 0)
            for p in stock_bajo_rows
        ]

        # Pedidos últimos 7 días (serie temporal)
        pedidos_7_dias = self.repo.get_pedidos_desde(self.session, semana_inicio)
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
