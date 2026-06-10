# features/auth/service.py - Servicio de autenticación
# AuthService gestiona registro (con verificación de email único + hash)
# y login (verifica credenciales, genera JWT, lo setea como cookie httponly).
# NO contiene consultas ORM directas — delega en AuthRepository.

from fastapi import HTTPException, Response, status
from sqlmodel import Session
from app.core.uow import UnitOfWork
from app.core.security import hash_password, verify_password, create_access_token
from app.features.auth.models import Usuario
from app.features.auth.schemas import AuthRegister, AuthLogin
from app.features.auth.repository import AuthRepository


class AuthService:
    """Servicio de autenticación: registro y login con JWT."""

    def __init__(self, uow: UnitOfWork, repo: AuthRepository):
        self.uow = uow
        self.repo = repo

    def register(self, data: AuthRegister) -> Usuario:
        """Registra un nuevo usuario con rol CLIENT automáticamente.
        Lanza: 409 si el email ya está registrado."""
        session: Session = self.uow.session

        existing = self.repo.get_by_email(session, data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El email ya está registrado",
            )

        user = Usuario(
            email=data.email,
            nombre=data.nombre,
            password_hash=hash_password(data.password),
        )
        session.add(user)
        session.flush()

        cliente_rol = self.repo.get_rol_cliente(session)
        if cliente_rol:
            user.rol_codigo = cliente_rol.codigo

        session.flush()
        session.refresh(user)
        return user

    def login(self, data: AuthLogin, response: Response) -> Usuario:
        """Autentica un usuario y setea cookie JWT httponly.
        Lanza: 401 si credenciales inválidas o usuario inactivo/eliminado."""
        session: Session = self.uow.session

        user = self.repo.get_by_email(session, data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )
        if not user.activo or user.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario inactivo o eliminado",
            )

        token = create_access_token({"user_id": user.id})
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            max_age=1800,
            samesite="lax",
        )
        return user
