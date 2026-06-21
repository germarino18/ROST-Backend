# ROST Backend API

LINK DEL VIDEO: https://www.youtube.com/watch?v=MrAY16nCnAo

Backend de la API REST para el proyecto ROST, construido utilizando **FastAPI** y **SQLModel**. Implementa una arquitectura robusta basada en repositorios y Unit of Work (UOW) para la persistencia en base de datos.

## Requisitos de Entorno

Asegurate de tener instalado:
- **Python 3.11+**
- **PostgreSQL** (en ejecución local o remoto)

---

## Configuración y Variables de Entorno (`.env`)

El servidor necesita variables de entorno para conectarse a la base de datos y comunicarse con servicios de terceros (Mercado Pago y Cloudinary). 

Crea un archivo `.env` en la raíz de la carpeta `backend/` usando el siguiente molde:

```env
# Base de datos PostgreSQL
DATABASE_URL=postgresql://<usuario>:<contraseña>@localhost:5432/parcial_db

# Seguridad y Autenticación (JWT)
SECRET_KEY=una_clave_secreta_super_segura_de_al_menos_32_caracteres
JWT_EXPIRATION_MINUTES=30

# Mercado Pago (Pasarela de Pagos)
MP_ACCESS_TOKEN=TEST-xxxx-tu-access-token
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000

# Cloudinary (Servicio de almacenamiento de imágenes)
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret
```

---

## Integración con Mercado Pago

Para procesar transacciones en la tienda, el backend interactúa con la API de Mercado Pago:
1. **Credenciales**: Necesitás ingresar a [Mercado Pago Developers](https://www.mercadopago.com.ar/developers/) con tu cuenta.
2. **Credenciales de prueba**: Ve a la sección de "Tus integraciones" -> selecciona o crea tu aplicación -> "Credenciales de prueba" (o producción si aplica).
3. **Access Token**: Copia el **Access Token** (suele empezar con `TEST-` o `APP_USR-`) y colócalo en `MP_ACCESS_TOKEN` dentro de tu archivo `.env`.
4. **URLs de retorno**: `FRONTEND_URL` y `BACKEND_URL` se utilizan para redirigir al usuario tras pagar y para gestionar los webhooks de notificación de pagos (IPN).

---

## Integración con Cloudinary (Imágenes)

Este proyecto requiere obligatoriamente Cloudinary para el manejo de imágenes de productos, ingredientes y categorías:
1. **Registro**: Crea una cuenta gratuita en [Cloudinary](https://cloudinary.com/).
2. **Credenciales**: En tu panel de control (Dashboard) vas a encontrar tu **Cloud Name**, **API Key** y **API Secret**.
3. **Configuración**: Copia estos tres valores y colocalos en sus respectivas variables en el archivo `.env`. Sin esto configurado correctamente, las funcionalidades de carga de imágenes en el panel administrativo van a fallar.

---

## Inicialización del Servidor Local

Seguí estos sencillos pasos para levantar el backend desde cero:

### 1. Preparar la Base de Datos
Asegurate de que PostgreSQL esté activo y creá la base de datos (por ejemplo, con el nombre `parcial_db`):
```powershell
psql -U postgres -c "CREATE DATABASE parcial_db;"
```

### 2. Crear y activar el entorno virtual de Python
Desde la carpeta `backend`:
```powershell
# En Windows (PowerShell):
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# En macOS/Linux:
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependencias
```powershell
pip install -r requirements.txt
```

### 4. Ejecutar el servidor
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Una vez levantado, podés acceder a:
- **Salud de la API**: [http://localhost:8000/](http://localhost:8000/)
- **Documentación interactiva (Swagger/OpenAPI)**: [http://localhost:8000/docs](http://localhost:8000/docs) (¡ideal para probar endpoints!)

> [!NOTE]  
> Al iniciar por primera vez, el backend crea de forma automática las tablas y ejecuta un script de siembra (`seed.py`) para precargar datos iniciales en la base de datos (roles, categorías de prueba, etc.).
