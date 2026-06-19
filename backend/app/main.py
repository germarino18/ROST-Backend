from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logger import get_logger, setup_logging
from app.core.middleware.logging_middleware import LoggingMiddleware
from app.core.middleware.timing_middleware import TimingMiddleware
from app.core.rate_limit.rate_limit_middleware import RateLimitMiddleware
from app.core.exceptions.exception_handlers import register_exception_handlers

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
from app.features.pagos.router import router as pagos_router
from app.features.images.router import router as images_router

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("app.startup — ROST V2")
    init_db()
    session = next(get_session())
    try:
        run_seed(session)
        logger.info("seed.completed")
    except Exception as e:
        logger.warning(f"seed.failed (continuamos sin seed): {e}")
    finally:
        session.close()
    yield
    logger.info("app.shutdown")


app = FastAPI(title="ROST V2 - API", lifespan=lifespan)

# ORDEN IMPORTANTE: rate limit primero, luego logging, luego timing, luego CORS
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(TimingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

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
app.include_router(pagos_router)
app.include_router(images_router)


@app.get("/")
def root():
    return {"message": "ROST V2 - API", "status": "ok"}
