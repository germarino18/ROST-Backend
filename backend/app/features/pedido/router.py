# features/pedido/router.py - Endpoints de pedidos
# GET   /api/v1/pedidos → Lista pedidos (CLIENT ve solo los suyos, ADMIN/PEDIDOS todos)
# GET   /api/v1/pedidos/{id} → Obtiene pedido (CLIENT solo si es suyo)
# POST  /api/v1/pedidos → Crea pedido (usuario autenticado)
# PATCH /api/v1/pedidos/{id}/estado → Avanza estado (requiere ADMIN o PEDIDOS)
# PATCH /api/v1/pedidos/{id}/cancelar → Cancela pedido (dueño del pedido)

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.db.database import get_session
from app.core.uow import UnitOfWork
from app.core.dependencies import get_current_user, require_role
from app.features.auth.models import Usuario
from app.features.pedido.schemas import PedidoCreate, PedidoRead, PedidoAccion
from app.features.pedido.service import PedidoService
from app.features.pedido.repository import PedidoRepository

router = APIRouter(prefix="/api/v1/pedidos", tags=["Pedidos"])


@router.get("", response_model=List[PedidoRead])
def listar_pedidos(
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """GET /api/v1/pedidos - Lista pedidos.
    CLIENT: solo sus pedidos. ADMIN/PEDIDOS/CAJERO/COCINERO: todos los pedidos."""
    role = current_user.rol_codigo
    with UnitOfWork(session) as uow:
        repo = PedidoRepository()
        service = PedidoService(uow, repo)
        if role in ("ADMIN", "PEDIDOS", "CAJERO", "COCINERO"):
            return service.get_all()
        return service.get_all(usuario_id=current_user.id)


@router.get("/{id}", response_model=PedidoRead)
def obtener_pedido(
    id: int,
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """GET /api/v1/pedidos/{id} - Obtiene pedido por ID.
    CLIENT: solo si es suyo. ADMIN/PEDIDOS/CAJERO/COCINERO: cualquier pedido."""
    with UnitOfWork(session) as uow:
        repo = PedidoRepository()
        service = PedidoService(uow, repo)
        pedido = service.get_by_id(id)
        role = current_user.rol_codigo
        if role not in ("ADMIN", "PEDIDOS", "CAJERO", "COCINERO"):
            if pedido.usuario_id != current_user.id:
                raise HTTPException(status_code=403, detail="No tienes acceso a este pedido")
        return pedido


@router.post("", response_model=PedidoRead, status_code=status.HTTP_201_CREATED)
async def crear_pedido(
    data: PedidoCreate,
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """POST /api/v1/pedidos - Crea un nuevo pedido (usuario autenticado).
    Recibe: items con producto_id y cantidad, más dirección y forma de pago.
    Descuenta stock automáticamente y emite broadcast WebSocket."""
    with UnitOfWork(session) as uow:
        repo = PedidoRepository()
        service = PedidoService(uow, repo)
        pedido, pedido_data, rooms = await service.create_and_broadcast(data, current_user.id)

    # Broadcast AFTER commit — el __exit__ del with ya hizo commit
    from app.core import manager as ws_manager
    event = {"type": "order_updated", "data": pedido_data}
    await ws_manager.broadcast_to_rooms(rooms, event)
    return pedido


@router.patch("/{id}/accion", response_model=PedidoRead)
async def ejecutar_accion(
    id: int,
    data: PedidoAccion,
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """PATCH /api/v1/pedidos/{id}/accion - Ejecuta una acción sobre el pedido.
    Valida estado actual + roles según ACCIONES definidas.
    Acciones: CONFIRMAR, PREPARAR, LISTO, ENTREGAR, CANCELAR."""
    with UnitOfWork(session) as uow:
        repo = PedidoRepository()
        service = PedidoService(uow, repo)
        pedido, pedido_data, rooms = await service.ejecutar_accion(
            id, data.accion, current_user.id, [current_user.rol_codigo]
        )

    # Broadcast AFTER commit
    from app.core import manager as ws_manager
    event = {"type": "order_updated", "data": pedido_data}
    await ws_manager.broadcast_to_rooms(rooms, event)
    return pedido


@router.patch("/{id}/cancelar", response_model=PedidoRead)
async def cancelar_pedido(
    id: int,
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """PATCH /api/v1/pedidos/{id}/cancelar - Cancela un pedido (atajo).
    Delega en la acción CANCELAR."""
    with UnitOfWork(session) as uow:
        repo = PedidoRepository()
        service = PedidoService(uow, repo)
        pedido, pedido_data, rooms = await service.ejecutar_accion(
            id, "CANCELAR", current_user.id, [current_user.rol_codigo]
        )

    # Broadcast AFTER commit
    from app.core import manager as ws_manager
    event = {"type": "order_updated", "data": pedido_data}
    await ws_manager.broadcast_to_rooms(rooms, event)
    return pedido
