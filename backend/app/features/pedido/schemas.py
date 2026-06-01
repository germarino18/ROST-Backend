# features/pedido/schemas.py - Schemas para pedidos
# PedidoCreate: creación con items (producto_id + cantidad), dirección y forma de pago
# PedidoUpdateEstado: cambio de estado (nuevo_estado)
# PedidoRead: respuesta con detalles, historial, total y estado actual

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, model_validator


class DetallePedidoItem(BaseModel):
    producto_id: int
    cantidad: int


class PedidoCreate(BaseModel):
    items: List[DetallePedidoItem]
    direccion_entrega_id: Optional[int] = None
    forma_pago_id: Optional[int] = None


class PedidoUpdateEstado(BaseModel):
    nuevo_estado: str


class DetallePedidoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    producto_id: int
    cantidad: int
    precio_snapshot: Optional[Decimal] = None
    nombre_snapshot: str
    personalizacion: Optional[Dict[str, Any]] = None


class HistorialEstadoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    estado: str
    cambiado_por: int
    fecha: Optional[datetime] = None


class PedidoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    usuario_nombre: str = ""
    direccion_entrega_id: Optional[int] = None
    forma_pago_id: Optional[int] = None
    estado_actual: str
    total: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    detalles: List[DetallePedidoRead] = []
    historial: List[HistorialEstadoRead] = []

    @model_validator(mode='before')
    @classmethod
    def populate_usuario_nombre(cls, data: Any) -> Any:
        """Si data es un Pedido (SQLModel), extrae usuario_nombre del relationship."""
        if hasattr(data, 'usuario') and hasattr(data, 'usuario_id'):
            _u = getattr(data, 'usuario', None)
            return {
                'id': data.id,
                'usuario_id': data.usuario_id,
                'usuario_nombre': _u.nombre if _u else "",
                'direccion_entrega_id': data.direccion_entrega_id,
                'forma_pago_id': data.forma_pago_id,
                'estado_actual': data.estado_actual,
                'total': data.total,
                'created_at': data.created_at,
                'updated_at': data.updated_at,
                'detalles': list(data.detalles or []),
                'historial': list(data.historial or []),
            }
        return data
