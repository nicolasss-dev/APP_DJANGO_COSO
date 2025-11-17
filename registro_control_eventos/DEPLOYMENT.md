# 🚀 Guía de Despliegue - PRCE

## Plataforma de Registro y Control de Eventos

Esta guía detalla el proceso de despliegue del sistema en diferentes entornos.

## 📋 Tabla de Contenidos

1. [Requisitos](#requisitos)
2. [Despliegue en Desarrollo](#despliegue-en-desarrollo)
3. [Despliegue en Producción](#despliegue-en-producción)
4. [Configuración de Servicios](#configuración-de-servicios)
5. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)

---

## Requisitos

### Software Necesario

- **Python**: 3.12 o superior
- **Base de Datos**: SQLite (desarrollo) o PostgreSQL 13+ (producción)
- **Servidor Web**: Nginx (recomendado)
- **WSGI Server**: Gunicorn
- **Sistema Operativo**: Linux (Ubuntu 20.04+ recomendado) o Windows Server

### Dependencias del Sistema

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.12 python3.12-venv python3-pip postgresql nginx

# CentOS/RHEL
sudo yum install python312 python312-pip postgresql-server nginx
```

---

## Despliegue en Desarrollo

### 1. Configuración Inicial

```bash
# Clonar repositorio
git clone <URL_REPOSITORIO>
cd DJANGO_FINAL_TEMPLATE/registro_control_eventos

# Crear entorno virtual
python3.12 -m venv venv

# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar configuración
nano .env
```

Configuración para desarrollo:
```env
DJANGO_ENV=development
DEBUG=True
SECRET_KEY=<generar-clave-segura>
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### 3. Inicializar Base de Datos

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Cargar datos iniciales (opcional)
python manage.py shell < crear_datos_iniciales.py
```

### 4. Iniciar Servidor de Desarrollo

```bash
python manage.py runserver
```

Acceder a: http://127.0.0.1:8000/

---

## Despliegue en Producción

### 1. Preparación del Servidor

```bash
# Actualizar sistema
sudo apt-get update && sudo apt-get upgrade -y

# Instalar dependencias
sudo apt-get install -y python3.12 python3.12-venv python3-pip \
    postgresql postgresql-contrib nginx supervisor git
```

### 2. Crear Usuario del Sistema

```bash
# Crear usuario dedicado
sudo adduser --system --group --home /opt/prce prce

# Cambiar a usuario prce
sudo su - prce
```

### 3. Clonar y Configurar Proyecto

```bash
# Clonar repositorio
cd /opt/prce
git clone <URL_REPOSITORIO> app
cd app/registro_control_eventos

# Crear entorno virtual
python3.12 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### 4. Configurar PostgreSQL

```bash
# Acceder a PostgreSQL
sudo -u postgres psql

# Crear base de datos y usuario
CREATE DATABASE prce_db;
CREATE USER prce_user WITH PASSWORD 'secure_password';
ALTER ROLE prce_user SET client_encoding TO 'utf8';
ALTER ROLE prce_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE prce_user SET timezone TO 'America/Bogota';
GRANT ALL PRIVILEGES ON DATABASE prce_db TO prce_user;
\q
```

### 5. Configurar Variables de Entorno

```bash
# Crear archivo .env
nano /opt/prce/app/registro_control_eventos/.env
```

Configuración para producción:
```env
DJANGO_ENV=production
DEBUG=False
SECRET_KEY=<GENERAR_CLAVE_SEGURA_COMPLEJA>
ALLOWED_HOSTS=tudominio.com,www.tudominio.com

# PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=prce_db
DB_USER=prce_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432

# Email SMTP
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password
DEFAULT_FROM_EMAIL=noreply@tudominio.com

# Seguridad
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

**Generar SECRET_KEY segura:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 6. Preparar Aplicación

```bash
# Aplicar migraciones
python manage.py migrate

# Colectar archivos estáticos
python manage.py collectstatic --noinput

# Crear directorios necesarios
mkdir -p /opt/prce/app/registro_control_eventos/logs
mkdir -p /opt/prce/app/registro_control_eventos/media/eventos/banners
mkdir -p /opt/prce/app/registro_control_eventos/media/certificados
mkdir -p /opt/prce/app/registro_control_eventos/media/pagos/comprobantes

# Establecer permisos
sudo chown -R prce:prce /opt/prce/app
```

### 7. Configurar Gunicorn

```bash
# Crear archivo de configuración
sudo nano /etc/supervisor/conf.d/prce.conf
```

Contenido:
```ini
[program:prce]
command=/opt/prce/app/registro_control_eventos/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/opt/prce/app/registro_control_eventos/prce.sock \
    registro_control_eventos.wsgi:application
directory=/opt/prce/app/registro_control_eventos
user=prce
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/prce/app/registro_control_eventos/logs/gunicorn.log
```

```bash
# Actualizar supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start prce
```

### 8. Configurar Nginx

```bash
# Crear configuración
sudo nano /etc/nginx/sites-available/prce
```

Contenido:
```nginx
server {
    listen 80;
    server_name tudominio.com www.tudominio.com;

    client_max_body_size 10M;

    location /static/ {
        alias /opt/prce/app/registro_control_eventos/staticfiles/;
    }

    location /media/ {
        alias /opt/prce/app/registro_control_eventos/media/;
    }

    location / {
        proxy_pass http://unix:/opt/prce/app/registro_control_eventos/prce.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/prce /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 9. Configurar SSL con Let's Encrypt

```bash
# Instalar Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d tudominio.com -d www.tudominio.com

# Renovación automática (ya configurada)
sudo certbot renew --dry-run
```

### 10. Configurar Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

---

## Configuración de Servicios

### Respaldos Automáticos

```bash
# Crear script de backup
sudo nano /opt/prce/backup.sh
```

Contenido:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/prce/backups"
mkdir -p $BACKUP_DIR

# Backup de base de datos
pg_dump prce_db > "$BACKUP_DIR/db_$DATE.sql"

# Backup de media files
tar -czf "$BACKUP_DIR/media_$DATE.tar.gz" /opt/prce/app/registro_control_eventos/media

# Eliminar backups antiguos (mantener últimos 30 días)
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completado: $DATE"
```

```bash
# Dar permisos
sudo chmod +x /opt/prce/backup.sh

# Configurar cron
sudo crontab -e

# Agregar línea para backup diario a las 3 AM
0 3 * * * /opt/prce/backup.sh >> /opt/prce/logs/backup.log 2>&1
```

### Monitoreo con Logs

```bash
# Ver logs de Gunicorn
tail -f /opt/prce/app/registro_control_eventos/logs/gunicorn.log

# Ver logs de Django
tail -f /opt/prce/app/registro_control_eventos/logs/django.log

# Ver logs de Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## Monitoreo y Mantenimiento

### Comandos Útiles

```bash
# Reiniciar servicios
sudo supervisorctl restart prce
sudo systemctl restart nginx

# Ver estado
sudo supervisorctl status
sudo systemctl status nginx

# Actualizar aplicación
cd /opt/prce/app/registro_control_eventos
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo supervisorctl restart prce
```

### Verificación de Salud

```bash
# Verificar configuración de Django
python manage.py check --deploy

# Verificar base de datos
python manage.py dbshell

# Verificar permisos
ls -la /opt/prce/app/registro_control_eventos/
```

### Optimización

```bash
# Limpiar sesiones expiradas
python manage.py clearsessions

# Optimizar base de datos PostgreSQL
sudo -u postgres psql prce_db -c "VACUUM ANALYZE;"
```

---

## Solución de Problemas Comunes

### Error 502 Bad Gateway
```bash
# Verificar que Gunicorn esté corriendo
sudo supervisorctl status prce

# Verificar permisos del socket
ls -la /opt/prce/app/registro_control_eventos/prce.sock
```

### Error de archivos estáticos
```bash
# Recolectar estáticos nuevamente
python manage.py collectstatic --clear --noinput

# Verificar configuración de Nginx
sudo nginx -t
```

### Error de conexión a base de datos
```bash
# Verificar que PostgreSQL esté corriendo
sudo systemctl status postgresql

# Verificar credenciales en .env
cat /opt/prce/app/registro_control_eventos/.env | grep DB_
```

---

## Seguridad

### Checklist de Seguridad

- [ ] SECRET_KEY fuerte y única
- [ ] DEBUG=False en producción
- [ ] HTTPS configurado con SSL
- [ ] Firewall configurado
- [ ] Permisos de archivos correctos
- [ ] Backups automáticos funcionando
- [ ] Actualizar dependencias regularmente
- [ ] Monitorear logs de seguridad

---

## Contacto y Soporte

Para soporte técnico o consultas sobre el despliegue:
- Email: soporte@prce.com
- Documentación: README.md

---

**Última actualización:** Noviembre 2025

