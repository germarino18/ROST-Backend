# features/auth/router.py - Endpoints de autenticación
# POST /api/v1/auth/register → Registro de nuevo usuario (público)
# POST /api/v1/auth/login → Login, setea cookie JWT (público)
# GET  /api/v1/auth/me → Devuelve el usuario autenticado (requiere cookie)
# POST /api/v1/auth/logout → Elimina la cookie JWT

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session
from app.db.database import get_session
from app.core.uow import UnitOfWork
from app.core.dependencies import get_current_user
from app.features.auth.schemas import AuthRegister, AuthLogin, AuthUserRead
from app.features.auth.service import AuthService
from app.features.auth.repository import AuthRepository
from app.features.auth.models import Usuario

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/register", response_model=AuthUserRead, status_code=status.HTTP_201_CREATED)
def register(data: AuthRegister, session: Session = Depends(get_session)):
    """POST /api/v1/auth/register - Registro público de nuevo usuario."""
    with UnitOfWork(session) as uow:
        repo = AuthRepository()
        service = AuthService(uow, repo)
        return service.register(data)


@router.post("/login", response_model=AuthUserRead)
def login(
    data: AuthLogin,
    response: Response,
    session: Session = Depends(get_session),
):
    """POST /api/v1/auth/login - Inicia sesión. Setea cookie httponly 'access_token'."""
    with UnitOfWork(session) as uow:
        repo = AuthRepository()
        service = AuthService(uow, repo)
        return service.login(data, response)


@router.get("/me", response_model=AuthUserRead)
def get_me(current_user: Usuario = Depends(get_current_user)):
    """GET /api/v1/auth/me - Devuelve el usuario autenticado."""
    return current_user


@router.post("/logout")
def logout(response: Response):
    """POST /api/v1/auth/logout - Cierra sesión eliminando la cookie."""
    response.delete_cookie(key="access_token")
    return {"message": "Sesión cerrada"}
