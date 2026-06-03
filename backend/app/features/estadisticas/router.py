from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.db.database import get_session
from app.core.dependencies import require_admin
from app.features.estadisticas.schemas import DashboardRead
from app.features.estadisticas.service import EstadisticasService

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


@router.get("/estadisticas", response_model=DashboardRead)
def get_dashboard(
    session: Session = Depends(get_session),
    _=Depends(require_admin),
):
    """GET /api/v1/admin/estadisticas - Dashboard con métricas del negocio.
    Requiere: rol ADMIN.
    Retorna: pedidos, ingresos, productos top, stock bajo, serie temporal."""
    service = EstadisticasService(session)
    return service.get_dashboard()