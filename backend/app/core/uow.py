# core/uow.py - Unit of Work (Patrón de diseño)
# Envuelve una sesión de SQLModel y provee commit/rollback automático.
# Al usarse como context manager (with), hace commit si no hay errores
# o rollback si ocurre una excepción.

from sqlmodel import Session


class UnitOfWork:
    """Unit of Work: encapsula una sesión de DB con commit/rollback automático.
    Al usarse como context manager (with), hace commit si no hay errores
    o rollback si ocurre una excepción."""

    def __init__(self, session: Session):
        self._session = session

    @property
    def session(self) -> Session:
        return self._session

    def commit(self):
        """Persiste los cambios pendientes en la DB."""
        self._session.commit()

    def rollback(self):
        """Descarta los cambios pendientes en la DB."""
        self._session.rollback()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
