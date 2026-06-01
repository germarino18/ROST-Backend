# features/usuario/models.py - Modelos de usuarios para administración
# Re-exporta los modelos Rol y UsuarioRol para que estén disponibles
# desde app.features.usuario.models.

from app.features.usuario.rol import Rol
from app.features.usuario.usuario_rol import UsuarioRol

__all__ = ["Rol", "UsuarioRol"]
