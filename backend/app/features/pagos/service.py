# features/pagos/service.py - Servicio de pagos con MercadoPago Checkout PRO
# NO hereda BaseService. NO llama self.uow.commit() — el commit lo hace el router
# vía "with UnitOfWork(session) as uow:".

import uuid
from typing import Optional
from fastapi import HTTPException, status
import mercadopago
from sqlmodel import Session
from app.core.uow import UnitOfWork
from app.core.config import MP_ACCESS_TOKEN, FRONTEND_URL, BACKEND_URL
from app.features.pagos.models import Pago
from app.features.pagos.repository import PagoRepository
from app.features.pedido.repository import PedidoRepository


class PagoService:
    """Servicio de pagos con MercadoPago.
    Crea preferencias de Checkout PRO y procesa webhooks de pago."""

    def __init__(self, uow: UnitOfWork, repo: PagoRepository):
        self.uow = uow
        self.repo = repo

    def crear_preference(self, pedido_id: int) -> dict:
        """Crea una preferencia de pago en MercadoPago para un pedido.
        1. Verifica que el pedido exista
        2. Verifica que no tenga ya un pago creado
        3. Llama a la API de MP para crear la preferencia
        4. Guarda el pago en BD con estado 'pending'
        5. Retorna {'preference_id': ..., 'init_point': ...}"""
        session = self.uow.session

        # 1. Verificar que el pedido existe
        pedido_repo = PedidoRepository()
        pedido = pedido_repo.get_by_id(session, pedido_id)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado",
            )

        # 2. Verificar que no tenga ya un pago
        pago_existente = self.repo.get_by_pedido_id(session, pedido_id)
        if pago_existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este pedido ya tiene un pago creado",
            )

        # 3-4. Generar claves de idempotencia
        idempotency_key = str(uuid.uuid4())
        external_reference = str(uuid.uuid4())

        # 5. Crear preferencia en MercadoPago
        sdk = mercadopago.SDK(MP_ACCESS_TOKEN)
        preference_data = {
            "items": [
                {
                    "title": f"Pedido #{pedido_id}",
                    "quantity": 1,
                    "unit_price": float(pedido.total) if pedido.total else 0,
                }
            ],
            "external_reference": external_reference,
            "back_urls": {
                "success": f"{FRONTEND_URL}/pago-exitoso",
                "failure": f"{FRONTEND_URL}/carrito",
                "pending": f"{FRONTEND_URL}/mis-pedidos",
            },
            "auto_return": "approved",
            "notification_url": f"{BACKEND_URL}/api/v1/pagos/webhook",
        }
        response = sdk.preference().create(preference_data)

        if response["status"] not in (200, 201):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error al crear preferencia en MercadoPago: {response['response']}",
            )

        mp_preference_id = response["response"]["id"]
        init_point = response["response"]["init_point"]

        # 6. Guardar el pago en BD
        pago = Pago(
            pedido_id=pedido_id,
            mp_preference_id=mp_preference_id,
            external_reference=external_reference,
            idempotency_key=idempotency_key,
            mp_status="pending",
        )
        session.add(pago)
        session.flush()
        session.refresh(pago)

        return {"preference_id": mp_preference_id, "init_point": init_point}

    def procesar_webhook(self, payment_id: int) -> dict:
        """Procesa un webhook de MercadoPago cuando un pago se actualiza.
        1. Consulta el pago en MP por payment_id
        2. Busca el Pago en BD por external_reference
        3. Actualiza los datos del pago en BD
        4. Si mp_status == 'approved': actualiza pedido a CONFIRMADO
        5. Retorna datos para broadcast"""
        session = self.uow.session

        # 1. Consultar el pago en MercadoPago
        sdk = mercadopago.SDK(MP_ACCESS_TOKEN)
        response = sdk.payment().get(payment_id)

        if response["status"] != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Error al consultar pago en MercadoPago",
            )

        payment_data = response["response"]
        external_reference = payment_data.get("external_reference")

        if not external_reference:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El pago no tiene external_reference",
            )

        # 2. Buscar el Pago en BD
        pago = self.repo.get_by_external_reference(session, external_reference)
        if not pago:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pago no encontrado para esta referencia",
            )

        # 3. Actualizar datos del pago
        pago.mp_payment_id = payment_id
        pago.mp_status = payment_data.get("status", "pending")
        pago.mp_status_detail = payment_data.get("status_detail")
        pago.transaction_amount = payment_data.get("transaction_amount")
        pago.payment_method_id = payment_data.get("payment_method_id")
        session.add(pago)
        session.flush()

        # 4. Si está aprobado, actualizar pedido
        pedido_data = None
        rooms = []
        if pago.mp_status == "approved":
            pedido_repo = PedidoRepository()
            pedido = pedido_repo.get_by_id(session, pago.pedido_id)
            if pedido:
                estado_anterior = pedido.estado_actual
                pedido.estado_actual = "CONFIRMADO"
                session.add(pedido)
                session.flush()

                # Crear registro en historial (cambiado_por=0 = sistema)
                pedido_repo.create_historial(
                    session,
                    pedido.id,
                    "CONFIRMADO",
                    0,
                )
                session.flush()
                session.refresh(pedido)

                # Serializar para broadcast
                from app.features.pedido.schemas import PedidoRead
                pedido_data = PedidoRead.model_validate(pedido).model_dump(mode="json")
                rooms = [
                    "role:ADMIN",
                    "role:PEDIDOS",
                    "role:CAJERO",
                    "role:COCINERO",
                    f"user:{pedido.usuario_id}",
                    f"order:{pedido.id}",
                ]

        # Refrescar el pago para incluir cambios
        session.flush()
        session.refresh(pago)

        return {
            "pago": pago,
            "pedido_data": pedido_data,
            "rooms": rooms,
        }

    def verificar_pago(self, payment_id: int) -> dict:
        """Verifica el estado REAL de un pago consultando directamente a MP.
        Se llama desde el frontend cuando el usuario vuelve del redirect de MP.
        NO confía en los query params de la URL — siempre consulta a MP API.

        A diferencia de procesar_webhook, solo actualiza si el estado cambió,
        para evitar duplicar entradas en el historial del pedido."""
        session = self.uow.session

        # 1. Consultar el pago en MercadoPago
        sdk = mercadopago.SDK(MP_ACCESS_TOKEN)
        response = sdk.payment().get(payment_id)

        if response["status"] != 200:
            return {"status": "error", "detail": "No se pudo verificar el pago en MercadoPago"}

        payment_data = response["response"]
        external_reference = payment_data.get("external_reference")

        if not external_reference:
            return {"status": "error", "detail": "El pago no tiene referencia externa"}

        # 2. Buscar el Pago en BD
        pago = self.repo.get_by_external_reference(session, external_reference)
        if not pago:
            return {"status": "not_found", "detail": "Pago no encontrado en el sistema"}

        mp_status = payment_data.get("status", "pending")

        # 3. Solo actualizar si cambió el estado (evita duplicar historial)
        pedido_actualizado = None
        if mp_status != pago.mp_status:
            pago.mp_payment_id = payment_id
            pago.mp_status = mp_status
            pago.mp_status_detail = payment_data.get("status_detail")
            pago.transaction_amount = payment_data.get("transaction_amount")
            pago.payment_method_id = payment_data.get("payment_method_id")
            session.add(pago)
            session.flush()

            # 4. Si está aprobado, actualizar pedido (solo si no estaba ya CONFIRMADO)
            if mp_status == "approved":
                pedido_repo = PedidoRepository()
                pedido = pedido_repo.get_by_id(session, pago.pedido_id)
                if pedido and pedido.estado_actual != "CONFIRMADO":
                    pedido.estado_actual = "CONFIRMADO"
                    session.add(pedido)
                    session.flush()
                    pedido_repo.create_historial(session, pedido.id, "CONFIRMADO", 0)
                    session.flush()
                    session.refresh(pedido)
                    # Serializar para broadcast
                    from app.features.pedido.schemas import PedidoRead
                    pedido_actualizado = PedidoRead.model_validate(pedido).model_dump(mode="json")

        result = {
            "status": "ok",
            "pago_status": mp_status,
            "payment_method_id": payment_data.get("payment_method_id"),
            "transaction_amount": payment_data.get("transaction_amount"),
        }

        # Si se actualizó el pedido, incluir datos para broadcast
        if pedido_actualizado:
            result["pedido_data"] = pedido_actualizado
            result["rooms"] = [
                "role:ADMIN",
                "role:PEDIDOS",
                "role:CAJERO",
                "role:COCINERO",
                f"user:{pedido.usuario_id}",
                f"order:{pedido.id}",
            ]

        return result
