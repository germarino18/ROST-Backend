# features/producto/schemas.py - Schemas para productos y relaciones M:N
# ProductoCreate: creación con nombre, precio, stock, categorías e ingredientes
# ProductoUpdate: actualización parcial (todos los campos opcionales)
# ProductoRead: respuesta con relaciones precargadas (categorías, ingredientes)

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.features.categoria.schemas import CategoriaRead
from app.features.ingrediente.schemas import IngredienteRead
from app.features.unidad_medida.schemas import UnidadMedidaRead


class ProductoCategoriaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    producto_id: int
    categoria_id: int
    es_principal: Optional[bool] = None
    created_at: Optional[datetime] = None
    categoria: Optional[CategoriaRead] = None


class ProductoIngredienteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    producto_id: int
    ingrediente_id: int
    cantidad: Optional[float] = None
    unidad_medida_id: int
    es_removible: Optional[bool] = None
    created_at: Optional[datetime] = None
    ingrediente: Optional[IngredienteRead] = None
    unidad_medida: Optional[UnidadMedidaRead] = None


class ProductoCreate(BaseModel):
    unidad_venta_id: Optional[int] = None
    nombre: str
    descripcion: Optional[str] = None
    precio_base: Optional[float] = None
    imagenes_url: Optional[List[str]] = None
    stock_cantidad: Optional[int] = 0
    disponible: Optional[bool] = True
    categorias: Optional[List[int]] = None
    ingredientes: Optional[List[dict]] = None


class ProductoUpdate(BaseModel):
    unidad_venta_id: Optional[int] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_base: Optional[float] = None
    imagenes_url: Optional[List[str]] = None
    stock_cantidad: Optional[int] = None
    disponible: Optional[bool] = None
    categorias: Optional[List[int]] = None
    ingredientes: Optional[List[dict]] = None


class ProductoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    unidad_venta_id: Optional[int] = None
    nombre: str
    descripcion: Optional[str] = None
    precio_base: Optional[float] = None
    imagenes_url: Optional[List[str]] = None
    stock_cantidad: Optional[int] = None
    disponible: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    categorias: Optional[List[ProductoCategoriaRead]] = Field(
        default=None, validation_alias="productos_categoria"
    )
    ingredientes: Optional[List[ProductoIngredienteRead]] = Field(
        default=None, validation_alias="productos_ingredientes"
    )
