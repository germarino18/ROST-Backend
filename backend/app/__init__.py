# app/__init__.py - Importa todos los modelos para que SQLAlchemy los registre
# Esto debe ejecutarse antes que cualquier importación de repositorios/routers
# para evitar errores de relaciones no resueltas (lazy string references).

from app.features.auth.models import Usuario
from app.features.usuario.rol import Rol
from app.features.usuario.usuario_rol import UsuarioRol
from app.features.categoria.models import Categoria
from app.features.ingrediente.models import Ingrediente
from app.features.producto.models import Producto, ProductoCategoria, ProductoIngrediente
from app.features.pedido.models import Pedido, DetallePedido, HistorialEstadoPedido, EstadoPedido
from app.features.direccion.models import DireccionEntrega
from app.features.forma_pago.models import FormaPago
from app.features.unidad_medida.models import UnidadMedida
