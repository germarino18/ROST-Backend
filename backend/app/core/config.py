# core/config.py - Configuración central del backend
# Define constantes desde variables de entorno para JWT (SECRET_KEY,
# algoritmo HS256, tiempo de expiración) y carga .env automáticamente.

import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "parcial-secret-key-change-in-prod")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "30"))
