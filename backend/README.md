# ROST Backend

## Descripción

Backend de la API REST construida con FastAPI y SQLModel. Incluye autenticación, manejo de usuarios, categorías, productos, pedidos, direcciones, formas de pago, unidades de medida y estadísticas.

## Requisitos

- Python 3.11+ (o compatible)
- PostgreSQL
- Git (opcional)

## Inicialización

1. Abre una terminal en la carpeta `backend`.
2. Crea y activa un entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Instala dependencias:

```powershell
pip install -r requirements.txt
```

## Configuración

El backend usa variables de entorno definidas en un archivo `.env`.

Crea un archivo `.env` en la carpeta `backend` con al menos estas variables:

```env
DATABASE_URL=postgresql://<usuario>:<contraseña>@<host>:<puerto>/<nombre_db>
SECRET_KEY=una_clave_secreta_para_jwt
JWT_EXPIRATION_MINUTES=30
```

Ejemplo local:

```env
DATABASE_URL=postgresql://postgres:cementista@localhost:5432/parcial_db
SECRET_KEY=parcial-secret-key-change-in-prod
JWT_EXPIRATION_MINUTES=30
```

> El valor por defecto de `DATABASE_URL` ya está definido en el código, pero es recomendable configurarlo explícitamente en `.env`.

## Base de datos

Asegúrate de tener PostgreSQL en ejecución y la base de datos creada.

Puedes crear la base de datos manualmente con un comando como:

```powershell
psql -U postgres -c "CREATE DATABASE parcial_db;"
```

## Ejecutar el servidor

Desde la carpeta `backend` y con el entorno virtual activado:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Luego abre en el navegador:

- `http://localhost:8000/` → endpoint raíz de salud
- `http://localhost:8000/docs` → documentación automática de OpenAPI

## Notas

- En el arranque, FastAPI crea las tablas de la base de datos y ejecuta un seed inicial usando `app/db/seed.py`.
- Si cambias modelos o la estructura de la DB, reinicia el servidor y PostgreSQL aplicará los cambios automáticos de creación de tablas.

## Estructura principal

- `app/main.py`: punto de entrada de la aplicación.
- `app/db/database.py`: configuración de la conexión con PostgreSQL.
- `app/core/config.py`: configuración JWT y carga de variables de entorno.
- `app/features/*`: rutas, servicios, repositorios y esquemas por dominio.

## Problemas comunes

- Si no puede conectar con PostgreSQL, revisa que `DATABASE_URL` sea correcto y que el servidor esté activo.
- Si falta alguna dependencia, ejecuta nuevamente:

```powershell
pip install -r requirements.txt
```
