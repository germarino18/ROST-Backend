# db/seed.py - Poblado inicial de la base de datos
# run_seed() ejecuta todas las funciones _seed_* en orden para crear:
# roles, formas de pago, estados de pedido, usuario admin por defecto,
# unidades de medida, categorías, ingredientes y productos de ejemplo.
# Cada función verifica si ya existen datos para evitar duplicados.

from sqlmodel import Session, select
from app.core.security import hash_password
from app.features.auth.models import Usuario
from app.features.usuario.rol import Rol
from app.features.categoria.models import Categoria
from app.features.ingrediente.models import Ingrediente
from app.features.producto.models import Producto, ProductoCategoria, ProductoIngrediente
from app.features.unidad_medida.models import UnidadMedida
from app.features.forma_pago.models import FormaPago
from app.features.pedido.models import EstadoPedido


def _seed_unidades_medida(session: Session):
    """Crea las unidades de medida base (kg, g, L, mL, pieza, docena, m²)."""
    if session.exec(select(UnidadMedida).limit(1)).first():
        return
    items = [
        UnidadMedida(nombre="kilogramo", simbolo="kg", tipo="masa"),
        UnidadMedida(nombre="gramo", simbolo="g", tipo="masa"),
        UnidadMedida(nombre="litro", simbolo="L", tipo="volumen"),
        UnidadMedida(nombre="mililitro", simbolo="mL", tipo="volumen"),
        UnidadMedida(nombre="pieza", simbolo="u", tipo="unidad"),
        UnidadMedida(nombre="docena", simbolo="doc", tipo="unidad"),
        UnidadMedida(nombre="metro cuadrado", simbolo="m²", tipo="area"),
    ]
    session.add_all(items)
    session.flush()


def _seed_categorias(session: Session):
    """Crea categorías de ejemplo: Cafés, Bebidas, Pastelería.
    Reemplaza datos placeholder si existen de seeds anteriores."""
    existing = session.exec(select(Categoria).limit(1)).first()
    if existing:
        old_names = {"Bebidas", "Lácteos", "Panadería"}
        if existing.nombre in old_names:
            for c in session.exec(select(Categoria)).all():
                session.delete(c)
            session.flush()
        else:
            return
    items = [
        Categoria(nombre="Cafés", descripcion="Cafés de especialidad y espresso"),
        Categoria(nombre="Bebidas", descripcion="Bebidas frías y otras preparaciones"),
        Categoria(nombre="Pastelería", descripcion="Croissants y acompañamientos"),
    ]
    session.add_all(items)
    session.flush()


def _seed_ingredientes(session: Session):
    """Crea ingredientes de ejemplo (café, leche, dulce de leche, etc.).
    Marca Harina y Huevo como alérgenos. Reemplaza datos placeholder."""
    existing = session.exec(select(Ingrediente).limit(1)).first()
    if existing:
        old_ingredients = {"Harina", "Azúcar", "Leche", "Huevo", "Sal", "Mantequilla"}
        if existing.nombre in old_ingredients:
            for i in session.exec(select(Ingrediente)).all():
                session.delete(i)
            session.flush()
        else:
            return
    items = [
        Ingrediente(nombre="Café en grano", descripcion="Café de especialidad tostado"),
        Ingrediente(nombre="Leche", descripcion="Leche entera"),
        Ingrediente(nombre="Dulce de leche", descripcion="Dulce de leche argentino"),
        Ingrediente(nombre="Cacao", descripcion="Cacao en polvo"),
        Ingrediente(nombre="Hielo", descripcion="Cubos de hielo"),
        Ingrediente(nombre="Harina", descripcion="Harina de trigo", es_alergeno=True),
        Ingrediente(nombre="Mantequilla", descripcion="Mantequilla sin sal"),
        Ingrediente(nombre="Huevo", descripcion="Huevo de gallina", es_alergeno=True),
    ]
    session.add_all(items)
    session.flush()


def _seed_productos(session: Session):
    """Crea productos de ejemplo (Café en granos, Expresso, Ice latte, etc.)
    junto con sus relaciones de categorías e ingredientes.
    Reemplaza datos placeholder si existen."""
    existing = session.exec(select(Producto).limit(1)).first()
    if existing:
        old_products = {"Pan Francés", "Pastel de Chocolate", "Leche Entera 1L"}
        if existing.nombre in old_products:
            for pc in session.exec(select(ProductoCategoria)).all():
                session.delete(pc)
            for pi in session.exec(select(ProductoIngrediente)).all():
                session.delete(pi)
            for p in session.exec(select(Producto)).all():
                session.delete(p)
            session.flush()
        else:
            return

    u = session.exec(select(UnidadMedida).where(UnidadMedida.simbolo == "u")).first()
    g = session.exec(select(UnidadMedida).where(UnidadMedida.simbolo == "g")).first()

    cafes_cat = session.exec(select(Categoria).where(Categoria.nombre == "Cafés")).first()
    bebidas_cat = session.exec(select(Categoria).where(Categoria.nombre == "Bebidas")).first()
    pasteleria_cat = session.exec(select(Categoria).where(Categoria.nombre == "Pastelería")).first()

    cafe_grano = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Café en grano")).first()
    leche = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Leche")).first()
    dlc = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Dulce de leche")).first()
    cacao = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Cacao")).first()
    hielo = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Hielo")).first()
    harina = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Harina")).first()
    mantequilla = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Mantequilla")).first()
    huevo = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Huevo")).first()

    # ── Productos ──────────────────────────────────────────
    cafe_granos = Producto(
        nombre="Café en granos",
        descripcion="Café de especialidad tostado artesanalmente. Bolsa de 250g de granos seleccionados.",
        precio_base=4500.00, stock_cantidad=30, disponible=True, unidad_venta_id=u.id,
        imagenes_url=[
            "https://thumbs.dreamstime.com/b/bolsitas-de-caf%C3%A9-generaci%C3%B3n-ia-los-granos-marr%C3%B3n-forman-un-fondo-denso-con-una-bolsa-papel-colocada-centralmente-en-la-parte-400978427.jpg"
        ],
    )
    expresso = Producto(
        nombre="Expresso cortado 120 ml",
        descripcion="Café expresso cortado con un toque de leche. Intenso y suave a la vez.",
        precio_base=1800.00, stock_cantidad=50, disponible=True, unidad_venta_id=u.id,
        imagenes_url=[
            "https://pedidosya.dhmedia.io/image/pedidosya/products/a9d7f79d-be5d-48d0-a45d-77ff453e84ae.jpg?quality=90&width=864&dpi=1.5"
        ],
    )
    ice_latte = Producto(
        nombre="Ice latte 350 ml",
        descripcion="Latte frío con hielo, perfecto para los días calurosos. Suave y refrescante.",
        precio_base=2800.00, stock_cantidad=40, disponible=True, unidad_venta_id=u.id,
        imagenes_url=[
            "https://pedidosya.dhmedia.io/image/pedidosya/products/88483610-7726-4ddf-8af0-1f10869d49f7.jpg?quality=90&width=1008&webp=1"
        ],
    )
    mokaccino = Producto(
        nombre="Mokaccino 350 ml",
        descripcion="Café con chocolate y leche. Una combinación irresistible.",
        precio_base=3000.00, stock_cantidad=40, disponible=True, unidad_venta_id=u.id,
        imagenes_url=[
            "https://pedidosya.dhmedia.io/image/pedidosya/products/94946615-5b77-4ee9-93b0-845594b7a220.jpg?quality=90&width=1008&webp=1"
        ],
    )
    latte = Producto(
        nombre="Latte 350 ml",
        descripcion="Clásico latte con café espresso y leche cremosa. Suave y equilibrado.",
        precio_base=2600.00, stock_cantidad=50, disponible=True, unidad_venta_id=u.id,
        imagenes_url=[
            "https://pedidosya.dhmedia.io/image/pedidosya/products/0d0b91c7-fdd9-4bfe-a24d-7e3754c5fdf4.jpg?quality=90&width=1008&webp=1"
        ],
    )
    croissant = Producto(
        nombre="Croissant de dulce de leche x2",
        descripcion="Croissant artesanal relleno de dulce de leche. Dos unidades.",
        precio_base=2200.00, stock_cantidad=25, disponible=True, unidad_venta_id=u.id,
        imagenes_url=[
            "https://pedidosya.dhmedia.io/image/pedidosya/products/51a450b9-7898-49f5-ab10-3df50209246c.jpg?quality=90&width=1008"
        ],
    )

    session.add_all([cafe_granos, expresso, ice_latte, mokaccino, latte, croissant])
    session.flush()

    # ── Categorías ─────────────────────────────────────────
    session.add_all([
        ProductoCategoria(producto_id=cafe_granos.id, categoria_id=cafes_cat.id, es_principal=True),
        ProductoCategoria(producto_id=expresso.id, categoria_id=cafes_cat.id, es_principal=True),
        ProductoCategoria(producto_id=mokaccino.id, categoria_id=cafes_cat.id, es_principal=True),
        ProductoCategoria(producto_id=latte.id, categoria_id=cafes_cat.id, es_principal=True),
        ProductoCategoria(producto_id=ice_latte.id, categoria_id=bebidas_cat.id, es_principal=True),
        ProductoCategoria(producto_id=croissant.id, categoria_id=pasteleria_cat.id, es_principal=True),
    ])

    # ── Ingredientes ───────────────────────────────────────
    session.add_all([
        ProductoIngrediente(producto_id=cafe_granos.id, ingrediente_id=cafe_grano.id, cantidad=250.000, unidad_medida_id=g.id, es_removible=False),
        ProductoIngrediente(producto_id=expresso.id, ingrediente_id=cafe_grano.id, cantidad=18.000, unidad_medida_id=g.id, es_removible=False),
        ProductoIngrediente(producto_id=expresso.id, ingrediente_id=leche.id, cantidad=30.000, unidad_medida_id=g.id, es_removible=False),
        ProductoIngrediente(producto_id=ice_latte.id, ingrediente_id=cafe_grano.id, cantidad=18.000, unidad_medida_id=g.id, es_removible=False),
        ProductoIngrediente(producto_id=ice_latte.id, ingrediente_id=leche.id, cantidad=200.000, unidad_medida_id=g.id, es_removible=True),
        ProductoIngrediente(producto_id=ice_latte.id, ingrediente_id=hielo.id, cantidad=6.000, unidad_medida_id=u.id, es_removible=False),
        ProductoIngrediente(producto_id=mokaccino.id, ingrediente_id=cafe_grano.id, cantidad=18.000, unidad_medida_id=g.id, es_removible=False),
        ProductoIngrediente(producto_id=mokaccino.id, ingrediente_id=leche.id, cantidad=200.000, unidad_medida_id=g.id, es_removible=True),
        ProductoIngrediente(producto_id=mokaccino.id, ingrediente_id=cacao.id, cantidad=15.000, unidad_medida_id=g.id, es_removible=False),
        ProductoIngrediente(producto_id=latte.id, ingrediente_id=cafe_grano.id, cantidad=18.000, unidad_medida_id=g.id, es_removible=False),
        ProductoIngrediente(producto_id=latte.id, ingrediente_id=leche.id, cantidad=200.000, unidad_medida_id=g.id, es_removible=True),
        ProductoIngrediente(producto_id=croissant.id, ingrediente_id=harina.id, cantidad=100.000, unidad_medida_id=g.id, es_removible=False),
        ProductoIngrediente(producto_id=croissant.id, ingrediente_id=mantequilla.id, cantidad=50.000, unidad_medida_id=g.id, es_removible=False),
        ProductoIngrediente(producto_id=croissant.id, ingrediente_id=dlc.id, cantidad=40.000, unidad_medida_id=g.id, es_removible=False),
        ProductoIngrediente(producto_id=croissant.id, ingrediente_id=huevo.id, cantidad=1.000, unidad_medida_id=u.id, es_removible=False),
    ])


def _seed_roles(session: Session):
    """Crea los roles del sistema si no existen (upsert individual)."""
    roles_data = [
        ("ADMIN", "Administrador"),
        ("STOCK", "Gestor de Stock"),
        ("PEDIDOS", "Gestor de Pedidos"),
        ("CAJERO", "Cajero"),
        ("COCINERO", "Cocinero"),
        ("CLIENT", "Cliente"),
    ]
    added = 0
    for codigo, descripcion in roles_data:
        existing = session.exec(select(Rol).where(Rol.codigo == codigo)).first()
        if not existing:
            session.add(Rol(codigo=codigo, descripcion=descripcion))
            added += 1
    if added:
        session.flush()


def _seed_formas_pago(session: Session):
    """Crea las formas de pago: Efectivo, Tarjeta de crédito, Transferencia, Mercado Pago."""
    if session.exec(select(FormaPago).limit(1)).first():
        return
    for nombre in ["Efectivo", "Tarjeta de crédito", "Transferencia", "Mercado Pago"]:
        session.add(FormaPago(nombre=nombre))
    session.flush()


def _seed_estados_pedido(session: Session):
    """Crea los estados de pedido: PENDIENTE, CONFIRMADO, EN_PREP, EN_CAMINO, ENTREGADO, CANCELADO."""
    if session.exec(select(EstadoPedido).limit(1)).first():
        return
    for codigo in ["PENDIENTE", "CONFIRMADO", "EN_PREP", "LISTO", "ENTREGADO", "CANCELADO"]:
        session.add(EstadoPedido(codigo=codigo))
    session.flush()


def _seed_admin_user(session: Session):
    """Crea el usuario admin por defecto (admin@store.com / admin1234)
    y le asigna el rol ADMIN."""
    if session.exec(select(Usuario).where(Usuario.email == "admin@store.com")).first():
        return
    admin = Usuario(
        nombre="Admin",
        email="admin@store.com",
        password_hash=hash_password("admin1234"),
        rol_codigo="ADMIN",
    )
    session.add(admin)


def run_seed(session: Session):
    """Ejecuta todos los seeds en orden de dependencia.
    Recibe: sesión de SQLModel.
    Commitea al final si todo sale bien."""
    _seed_roles(session)
    _seed_formas_pago(session)
    _seed_estados_pedido(session)
    _seed_admin_user(session)
    _seed_unidades_medida(session)
    _seed_categorias(session)
    _seed_ingredientes(session)
    _seed_productos(session)
    session.commit()
