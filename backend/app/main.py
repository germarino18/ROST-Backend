# main.py - Punto de entrada de la aplicación FastAPI
# Configura CORS para los frontends, registra todos los routers
# bajo /api/v1, y en el startup inicializa la DB y ejecuta el seed.

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from app.db.database import init_db, get_session
from app.db.seed import run_seed
from app.features.auth.router import router as auth_router
from app.features.categoria.router import router as categoria_router
from app.features.usuario.router import router as usuario_router
from app.features.producto.router import router as producto_router
from app.features.ingrediente.router import router as ingrediente_router
from app.features.pedido.router import router as pedido_router
from app.features.pedido.websocket import router as pedido_websocket_router
from app.features.direccion.router import router as direccion_router
from app.features.forma_pago.router import router as forma_pago_router
from app.features.unidad_medida.router import router as unidad_medida_router
from app.features.estadisticas.router import router as estadisticas_router

app = FastAPI(title="ROST V2 - API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(categoria_router)
app.include_router(usuario_router)
app.include_router(producto_router)
app.include_router(ingrediente_router)
app.include_router(pedido_router)
app.include_router(pedido_websocket_router)
app.include_router(direccion_router)
app.include_router(forma_pago_router)
app.include_router(unidad_medida_router)
app.include_router(estadisticas_router)


@app.on_event("startup")
def on_startup():
    """Evento de inicio de FastAPI: crea tablas y ejecuta seed de datos iniciales."""
    init_db()
    session = next(get_session())
    try:
        run_seed(session)
    finally:
        session.close()


@app.get("/")
def root():
    """GET / - Endpoint raíz de salud."""
    return {"message": "ROST V2 - API"}
