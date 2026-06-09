# features/pedido/service.py - Servicio de pedidos
# NO hereda BaseService. Gestiona: creación con transacción y descuento de stock,
# máquina de estados (avanzar_estado), y cancelación.
# NO contiene consultas ORM directas — delega en PedidoRepository.

from typing import List, Optional
from fastapi import HTTPException, status
from app.core.uow import UnitOfWork
from app.features.pedido.models import Pedido
from app.features.pedido.schemas import PedidoCreate, PedidoAccion
from app.features.pedido.repository import PedidoRepository

ACCIONES = {
    "CONFIRMAR": {"origen": ["PENDIENTE"],               "destino": "CONFIRMADO", "roles": ["ADMIN", "PEDIDOS", "CAJERO"]},
    "PREPARAR":  {"origen": ["CONFIRMADO", "EN_CAMINO"],  "destino": "EN_PREP",   "roles": ["ADMIN", "COCINERO"]},
    "LISTO":     {"origen": ["EN_PREP"],                   "destino": "LISTO",     "roles": ["ADMIN", "COCINERO"]},
    "ENTREGAR":  {"origen": ["LISTO"],                     "destino": "ENTREGADO", "roles": ["ADMIN", "PEDIDOS", "CAJERO"]},
    "CANCELAR":  {"origen": ["PENDIENTE", "CONFIRMADO"],   "destino": "CANCELADO", "roles": ["ADMIN", "PEDIDOS", "CAJERO"]},
}


class PedidoService:
    """Servicio de pedidos. NO hereda BaseService.
    Gestiona: creación con transacción y descuento de stock,
    máquina de estados (avanzar_estado), y cancelación."""

    def __init__(self, uow: UnitOfWork, repo: PedidoRepository):
        self.uow = uow
        self.repo = repo

    def get_all(self, usuario_id: Optional[int] = None) -> List[Pedido]:
        return self.repo.get_all(self.uow.session, usuario_id=usuario_id)

    def get_by_id(self, id: int) -> Pedido:
        pedido = self.repo.get_by_id_with_relations(self.uow.session, id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        return pedido

    def create(self, data: PedidoCreate, usuario_id: int) -> Pedido:
        """Versión sync — usada por el endpoint sincrónico.
        Retorna el pedido creado SIN broadcast WS."""
        session = self.uow.session

        pedido = Pedido(
            usuario_id=usuario_id,
            direccion_entrega_id=data.direccion_entrega_id,
            forma_pago_id=data.forma_pago_id,
            estado_actual="PENDIENTE",
            total=0,
        )
        session.add(pedido)
        session.flush()

        total = 0
        for item in data.items:
            producto = self.repo.get_producto(session, item.producto_id)
            if not producto:
                raise HTTPException(
                    status_code=404,
                    detail=f"Producto {item.producto_id} no encontrado",
                )
            if (
                producto.stock_cantidad is not None
                and item.cantidad > producto.stock_cantidad
            ):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Stock insuficiente para {producto.nombre}: solicitado {item.cantidad}, disponible {producto.stock_cantidad}",
                )

            self.repo.create_detalle(
                session,
                pedido_id=pedido.id,
                producto_id=item.producto_id,
                cantidad=item.cantidad,
                precio_snapshot=producto.precio_base,
                nombre_snapshot=producto.nombre,
            )

            self.repo.update_producto_stock(session, producto, item.cantidad)

            if producto.precio_base:
                total += float(producto.precio_base) * item.cantidad

        pedido.total = total
        session.add(pedido)
        session.flush()

        self.repo.create_historial(
            session, pedido.id, "PENDIENTE", usuario_id
        )

        session.flush()
        session.refresh(pedido)
        self.uow.commit()
        return pedido

    async def create_and_broadcast(self, data: PedidoCreate, usuario_id: int) -> Pedido:
        """Versión async — crea el pedido y emite broadcast WS.
        Usada por el endpoint async."""
        pedido = self.create(data, usuario_id)

        # Broadcast a todos los roles relevantes
        from app.features.pedido.schemas import PedidoRead
        pedido_data = PedidoRead.model_validate(pedido).model_dump(mode="json")
        rooms = [
            "role:ADMIN",
            "role:PEDIDOS",
            "role:CAJERO",
            "role:COCINERO",
            f"user:{usuario_id}",
        ]
        from app.core import manager as ws_manager
        event = {"type": "order_updated", "data": pedido_data}
        await ws_manager.broadcast_to_rooms(rooms, event)

        return pedido

    @staticmethod
    def _build_rooms(pedido_id: int, usuario_id: int, accion: str) -> list[str]:
        """Construye las salas a las que broadcastear según la acción."""
        ROLE_ROOMS = {
            "CONFIRMAR": ["role:COCINERO", "role:ADMIN", "role:PEDIDOS", "role:CAJERO"],
            "PREPARAR": ["role:ADMIN", "role:PEDIDOS", "role:CAJERO"],
            "LISTO": ["role:CAJERO", "role:ADMIN", "role:PEDIDOS", "role:COCINERO"],
            "ENTREGAR": ["role:ADMIN", "role:PEDIDOS", "role:COCINERO"],
            "CANCELAR": ["role:ADMIN", "role:PEDIDOS", "role:COCINERO", "role:CAJERO"],
        }
        rooms = [f"order:{pedido_id}", f"user:{usuario_id}"]
        rooms.extend(ROLE_ROOMS.get(accion, []))
        return rooms

    async def ejecutar_accion(
        self, pedido_id: int, accion: str, usuario_id: int, roles_usuario: list[str]
    ) -> Pedido:
        """Ejecuta una acción validando estado actual + roles del usuario.
        Si el usuario tiene rol ADMIN, salta toda validación de roles."""
        if accion not in ACCIONES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Acción '{accion}' no válida",
            )

        accion_info = ACCIONES[accion]
        session = self.uow.session

        # Usar get_by_id_with_relations para que el pedido traiga detalles e historial
        pedido = self.repo.get_by_id_with_relations(session, pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        # Validar estado origen
        if pedido.estado_actual not in accion_info["origen"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"No se puede ejecutar '{accion}' en estado {pedido.estado_actual}",
            )

        # Validar roles (ADMIN siempre puede)
        if "ADMIN" not in roles_usuario:
            tiene_rol = any(r in roles_usuario for r in accion_info["roles"])
            if not tiene_rol:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"No tenés permisos para ejecutar '{accion}'",
                )

        nuevo_estado = accion_info["destino"]
        pedido.estado_actual = nuevo_estado
        session.add(pedido)

        self.repo.create_historial(session, pedido_id, nuevo_estado, usuario_id)

        # Serializar datos del pedido ANTES del commit (mientras la sesión está abierta)
        session.flush()
        session.refresh(pedido)
        from app.features.pedido.schemas import PedidoRead
        pedido_data = PedidoRead.model_validate(pedido).model_dump(mode="json")
        rooms = self._build_rooms(pedido_id, pedido.usuario_id, accion)
        self.uow.commit()

        # Broadcast AFTER commit — los datos ya están serializados
        from app.core import manager as ws_manager
        event = {"type": "order_updated", "data": pedido_data}
        await ws_manager.broadcast_to_rooms(rooms, event)

        return pedido


