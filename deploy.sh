#!/bin/bash
# Script de despliegue para PRCE
# Uso: ./deploy.sh [development|production]

set -e

ENVIRONMENT=${1:-development}

echo "==================================="
echo "PRCE - Script de Despliegue"
echo "Entorno: $ENVIRONMENT"
echo "==================================="

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
log() {
    echo -e "${GREEN}[✓]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# 1. Verificar Python
log "Verificando Python 3.12+..."
python --version

# 2. Activar entorno virtual (si existe)
if [ -d "venv" ]; then
    log "Activando entorno virtual..."
    source venv/bin/activate
else
    warn "No se encontró entorno virtual. Creando uno nuevo..."
    python -m venv venv
    source venv/bin/activate
fi

# 3. Instalar dependencias
log "Instalando dependencias..."
pip install -r requirements.txt

# 4. Verificar archivo .env
if [ ! -f ".env" ]; then
    warn "Archivo .env no encontrado. Copiando desde .env.example..."
    cp .env.example .env
    warn "Por favor configure el archivo .env antes de continuar."
    exit 1
fi

# 5. Aplicar migraciones
log "Aplicando migraciones..."
python manage.py makemigrations
python manage.py migrate

# 6. Colectar archivos estáticos
if [ "$ENVIRONMENT" = "production" ]; then
    log "Colectando archivos estáticos..."
    python manage.py collectstatic --noinput
fi

# 7. Crear superusuario (solo en desarrollo)
if [ "$ENVIRONMENT" = "development" ]; then
    log "¿Desea crear un superusuario? (s/n)"
    read -r response
    if [ "$response" = "s" ]; then
        python manage.py createsuperuser
    fi
fi

# 8. Verificar configuración
log "Verificando configuración del sistema..."
python manage.py check --deploy

log "========================================="
log "Despliegue completado exitosamente!"
log "========================================="

if [ "$ENVIRONMENT" = "development" ]; then
    log "Para iniciar el servidor de desarrollo:"
    log "  python manage.py runserver"
else
    log "Para iniciar con Gunicorn:"
    log "  gunicorn config.wsgi:application --bind 0.0.0.0:8000"
fi

