from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlmodel import Session
from app.db.database import engine
from app.core.security import decode_access_token
from app.features.auth.models import Usuario
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/api/v1/pedidos/ws")
async def pedidos_websocket(websocket: WebSocket):
    # Acepta token de cookie (mismo origen) o query param (origen cruzado, ej: ngrok)
    cookies = websocket.cookies
    token = cookies.get("access_token") or websocket.query_params.get("token")

    if not token:
        await websocket.close(code=4001, reason="No autenticado")
        return

    payload = decode_access_token(token)
    if payload is None:
        await websocket.close(code=4001, reason="Token inválido")
        return

    user_id = payload.get("user_id")
    if user_id is None:
        await websocket.close(code=4001, reason="Token inválido")
        return

    with Session(engine) as session:
        user = session.get(Usuario, user_id)
        if not user or not user.activo or user.deleted_at is not None:
            await websocket.close(code=4001, reason="Usuario no válido")
            return
        rol_codigo = user.rol_codigo

    from app.core import manager as ws_manager

    await ws_manager.connect(websocket)

    # Unirse a rooms por rol y por usuario (para notificar al dueño del pedido)
    await ws_manager.join_room(f"role:{rol_codigo}", websocket) if rol_codigo else None
    await ws_manager.join_room(f"user:{user_id}", websocket)
    logger.info(f"WebSocket conectado: user={user_id} role={rol_codigo}")

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info(f"WebSocket desconectado: user={user_id}")
        await ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Error en WebSocket: {e}")
        await ws_manager.disconnect(websocket)
