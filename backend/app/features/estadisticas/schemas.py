from decimal import Decimal
from typing import Dict, List, Optional
from pydantic import BaseModel


class ProductoTop(BaseModel):
    nombre: str
    cantidad: int


class StockBajo(BaseModel):
    nombre: str
    stock: int


class PedidoDiario(BaseModel):
    fecha: str
    total: int


class DashboardRead(BaseModel):
    pedidos_hoy: int = 0
    ingresos_hoy: float = 0
    pedidos_semana: int = 0
    ingresos_semana: float = 0
    pedidos_por_estado: Dict[str, int] = {}
    productos_mas_vendidos: List[ProductoTop] = []
    stock_bajo: List[StockBajo] = []
    pedidos_ultimos_7_dias: List[PedidoDiario] = []
