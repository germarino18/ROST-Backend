# features/pagos/router.py - Endpoints de pagos
# POST /api/v1/pagos/crear → Crea preferencia de pago (CLIENT)
# POST /api/v1/pagos/webhook → Webhook de MercadoPago (público)
# GET  /api/v1/pagos/{pedido_id} → Obtener pago por pedido

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session
from app.db.database import get_session
from app.core.uow import UnitOfWork
from app.core.dependencies import get_current_user, require_any_role
from app.features.auth.models import Usuario
from app.features.pagos.schemas import (
    CrearPreferenceRequest,
    CrearPreferenceResponse,
    PagoRead,
    WebhookPayload,
)
from app.features.pagos.service import PagoService
from app.features.pagos.repository import PagoRepository

router = APIRouter(prefix="/api/v1/pagos", tags=["Pagos"])


@router.post("/crear", response_model=CrearPreferenceResponse, status_code=status.HTTP_201_CREATED)
def crear_preference(
    data: CrearPreferenceRequest,
    current_user: Usuario = Depends(require_any_role("ADMIN", "CLIENT", "CAJERO")),
    session: Session = Depends(get_session),
):
    """POST /api/v1/pagos/crear - Crea una preferencia de pago en MercadoPago.
    Requiere autenticación (CLIENT, CAJERO o ADMIN).
    Retorna el ID de preferencia y el init_point para redirigir al checkout."""
    with UnitOfWork(session) as uow:
        repo = PagoRepository()
        service = PagoService(uow, repo)
        result = service.crear_preference(data.pedido_id)
    return result


@router.post("/webhook")
async def webhook_mercadopago(
    request: Request,
    session: Session = Depends(get_session),
):
    """POST /api/v1/pagos/webhook - Webhook de MercadoPago (público).
    MercadoPago puede enviar el payload como:
    - Query params: ?type=payment&data.id=123
    - JSON body: {"type": "payment", "data": {"id": 123}}
    Retorna siempre 200 para que MP no reintente."""
    query_params = dict(request.query_params)
    payment_id = None

    if "data.id" in query_params:
        try:
            payment_id = int(query_params["data.id"])
        except (ValueError, TypeError):
            pass

    if payment_id is None:
        try:
            body = await request.json()
            if body.get("type") == "payment":
                data = body.get("data", {})
                if isinstance(data, dict):
                    payment_id = int(data.get("id", 0))
                elif isinstance(data, (int, str)):
                    payment_id = int(data)
        except Exception:
            pass

    if not payment_id:
        return {"status": "ok", "detail": "No payment_id received"}

    with UnitOfWork(session) as uow:
        repo = PagoRepository()
        service = PagoService(uow, repo)
        result = service.procesar_webhook(payment_id)

    if result.get("pedido_data") and result.get("rooms"):
        from app.core import manager as ws_manager
        event = {"type": "order_updated", "data": result["pedido_data"]}
        await ws_manager.broadcast_to_rooms(result["rooms"], event)

    return {"status": "ok"}


@router.post("/verificar/{payment_id}")
async def verificar_pago(
    payment_id: int,
    session: Session = Depends(get_session),
):
    """POST /api/v1/pagos/verificar/{payment_id} - Verifica el estado REAL de un pago
    consultando a MercadoPago directamente. Público, llamado desde la SuccessPage
    después del redirect de MP. NO confía en los query params de la URL."""
    with UnitOfWork(session) as uow:
        repo = PagoRepository()
        service = PagoService(uow, repo)
        result = service.verificar_pago(payment_id)

    # Broadcast si se actualizó el pedido (pago aprobado)
    if result.get("pedido_data") and result.get("rooms"):
        from app.core import manager as ws_manager
        event = {"type": "order_updated", "data": result["pedido_data"]}
        await ws_manager.broadcast_to_rooms(result["rooms"], event)

    return result


@router.get("/{pedido_id}", response_model=PagoRead)
def obtener_pago_por_pedido(
    pedido_id: int,
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """GET /api/v1/pagos/{pedido_id} - Obtiene el pago asociado a un pedido.
    CLIENT: solo si el pedido le pertenece. ADMIN: cualquier pedido."""
    with UnitOfWork(session) as uow:
        repo = PagoRepository()
        service = PagoService(uow, repo)
        pago = repo.get_by_pedido_id(session, pedido_id)

    if not pago:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pago no encontrado para este pedido",
        )

    if current_user.rol_codigo not in ("ADMIN",):
        from app.features.pedido.repository import PedidoRepository
        pedido_repo = PedidoRepository()
        pedido = pedido_repo.get_by_id(session, pedido_id)
        if not pedido or pedido.usuario_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a este pago",
            )

    return pago
