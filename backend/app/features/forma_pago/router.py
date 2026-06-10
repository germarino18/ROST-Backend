# features/forma_pago/router.py - Endpoints de formas de pago
# GET /api/v1/formas-pago → Lista formas de pago disponibles (público)

from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.db.database import get_session
from app.core.uow import UnitOfWork
from app.features.forma_pago.schemas import FormaPagoCreate, FormaPagoRead
from app.features.forma_pago.service import FormaPagoService
from app.features.forma_pago.repository import FormaPagoRepository

router = APIRouter(prefix="/api/v1/formas-pago", tags=["Formas de Pago"])


@router.get("", response_model=List[FormaPagoRead])
def listar_formas_pago(
    session: Session = Depends(get_session),
):
    """GET /api/v1/formas-pago - Lista formas de pago disponibles (público)."""
    with UnitOfWork(session) as uow:
        repo = FormaPagoRepository()
        service = FormaPagoService(uow, repo)
        return service.get_all()
