# Guía de Instalación y Configuración - PRCE

## Requisitos Previos

- Python 3.12 o superior
- pip (gestor de paquetes)
- Git (opcional)

## Pasos de Instalación

### 1. Clonar o descargar el proyecto

```bash
cd DJANGO_FINAL_TEMPLATE/registro_control_eventos
```

### 2. Crear y activar entorno virtual (IMPORTANTE)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno (Opcional)

Por defecto el proyecto funciona con SQLite y configuración de desarrollo.

Para producción, copiar `.env.template` a `.env` y configurar:
```bash
cp .env.template .env
# Editar .env con tus configuraciones
```

### 5. Aplicar migraciones

```bash
python manage.py migrate
```

### 6. Crear datos iniciales

```bash
python manage.py shell < crear_datos_iniciales.py
```

Esto creará:
- Usuario administrador: `admin` / `admin123`
- Tipos de eventos
- Tipos de notificaciones
- Plantillas de correo
- Métodos de pago

### 7. Ejecutar servidor de desarrollo

```bash
python manage.py runserver
```

### 8. Acceder a la aplicación

Abrir navegador en:
- **Aplicación principal**: http://127.0.0.1:8000/
- **Panel Admin**: http://127.0.0.1:8000/admin/

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `admin123`

## Configuración Adicional

### Crear superusuario manualmente

Si necesitas crear otro administrador:

```bash
python manage.py createsuperuser
```

### Colectar archivos estáticos

Para producción:

```bash
python manage.py collectstatic
```

### Configurar Email

Editar `.env` y configurar:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password
DEFAULT_FROM_EMAIL=noreply@prce.com
```

**Nota para Gmail**: Debes generar una "Contraseña de Aplicación" desde la configuración de seguridad de tu cuenta Google.

### Configurar Base de Datos PostgreSQL

1. Instalar psycopg2:
```bash
pip install psycopg2-binary
```

2. Editar `.env`:
```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=prce_db
DB_USER=prce_user
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
```

3. Ejecutar migraciones:
```bash
python manage.py migrate
```

## Solución de Problemas

### Error: "No module named 'dotenv'"

```bash
pip install python-dotenv
```

### Error: "No such file or directory: logs/django.log"

```bash
mkdir logs
```

### Error con permisos en Windows

Ejecutar PowerShell como Administrador.

### Error con imágenes

Instalar Pillow:
```bash
pip install Pillow
```

### Error con ReportLab (PDFs)

```bash
pip install reportlab
```

## Próximos Pasos

1. Cambiar la contraseña del administrador
2. Crear usuarios organizadores y asistentes
3. Configurar plantillas de correo
4. Crear primer evento de prueba
5. Probar flujo completo de inscripción

## Soporte

Para más información, consultar `README.md` o contactar al equipo de desarrollo.

---

**IMPORTANTE**: Cambiar `SECRET_KEY` y `DEBUG=False` en producción.

