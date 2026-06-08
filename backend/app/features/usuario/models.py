# features/usuario/models.py - Modelos de usuarios para administración
# Re-exporta el modelo Rol para que esté disponible
# desde app.features.usuario.models.

from app.features.usuario.rol import Rol

__all__ = ["Rol"]
