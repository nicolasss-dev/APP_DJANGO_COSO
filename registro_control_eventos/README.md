# Plataforma Web de Registro y Control de Eventos (PRCE)

## Descripción

Sistema web desarrollado con Django 5.x para la gestión integral de eventos, inscripciones, control de asistencia y generación de certificados.

**Proyecto educativo** - Ingeniería de Requisitos

## Stack Tecnológico

- **Framework Backend**: Django 5.2.8
- **Lenguaje**: Python 3.12+
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Generación PDFs**: ReportLab
- **Códigos QR**: qrcode
- **Protocolo**: HTTPS obligatorio en producción

## Características Principales

### Módulo 1: Gestión de Eventos
- ✅ Creación, edición y eliminación de eventos
- ✅ Clasificación por tipo (Académico, Cultural, Corporativo, Deportivo, Social)
- ✅ Subida de imágenes promocionales
- ✅ Duplicación de eventos
- ✅ Control de estados (Borrador, Publicado, En Curso, Finalizado, Cancelado)

### Módulo 2: Gestión de Usuarios
- ✅ Sistema de autenticación seguro
- ✅ Tres roles: Administrador, Organizador, Asistente
- ✅ Gestión de perfiles
- ✅ Activación/desactivación de usuarios
- ✅ Historial de cambios de rol

### Módulo 3: Inscripciones
- ✅ Registro público sin autenticación
- ✅ Registro masivo mediante Excel/CSV
- ✅ Validación de cupos
- ✅ Estados: Pendiente, Confirmada, Cancelada, Rechazada
- ✅ Generación de códigos QR únicos

### Módulo 4: Control de Asistencia
- ✅ Registro manual por organizadores
- ✅ Escaneo de código QR
- ✅ Cálculo automático de porcentaje de asistencia
- ✅ Control por sesiones
- ✅ Estadísticas en tiempo real

### Módulo 5: Certificados
- ✅ Generación automática de PDFs
- ✅ Código de verificación único
- ✅ Envío automático por correo
- ✅ Plantillas personalizables
- ✅ Validación de asistencia mínima (80%)

### Módulo 6: Notificaciones
- ✅ Confirmación de inscripción
- ✅ Recordatorios automáticos previos
- ✅ Notificación de cambios/cancelaciones
- ✅ Plantillas de correo configurables
- ✅ Variables dinámicas

### Módulo 7: Pagos
- ✅ Registro manual de pagos
- ✅ Múltiples métodos: Efectivo, Transferencia, Tarjeta, Pasarela
- ✅ Adjuntar comprobantes
- ✅ Preparación para integración con pasarelas
- ✅ Reportes financieros por evento

### Módulo 8: Reportes y Estadísticas
- ✅ Dashboard con métricas principales
- ✅ Reportes de asistencia
- ✅ Reportes financieros
- ✅ Exportación a PDF y Excel
- ✅ Gráficos y visualizaciones

### Módulo 9: Requisitos No Funcionales
- ✅ Interfaz accesible (WCAG AA)
- ✅ Diseño responsive
- ✅ Rendimiento optimizado
- ✅ Seguridad: HTTPS, CSRF, hashing de contraseñas
- ✅ Protección de datos personales
- ✅ Logging de eventos
- ✅ Compatible con navegadores modernos

## Instalación y Configuración

### Prerrequisitos

Antes de comenzar, asegúrate de tener instalado:

- **Python 3.12 o superior** - [Descargar](https://www.python.org/downloads/)
- **pip** (viene incluido con Python)
- **Git** - [Descargar](https://git-scm.com/)
- **Editor de código** (recomendado: VS Code, PyCharm)

### Guía de Instalación Paso a Paso

#### 1. Clonar el Repositorio

Abre tu terminal o línea de comandos y ejecuta:

```bash
git clone https://github.com/nicolasss-dev/APP_DJANGO_COSO.git
cd APP_DJANGO_COSO
```

#### 2. Navegar al Directorio del Proyecto

```bash
cd registro_control_eventos
```

Tu ubicación actual debe ser: `APP_DJANGO_COSO/registro_control_eventos/`

#### 3. Crear Entorno Virtual

Es **fundamental** trabajar con un entorno virtual para aislar las dependencias del proyecto.

**Windows:**
```bash
python -m venv venv
```

**Linux/Mac:**
```bash
python3 -m venv venv
```

#### 4. Activar el Entorno Virtual

**Windows (PowerShell):**
```bash
venv\Scripts\activate
```

**Windows (CMD):**
```bash
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

> **Nota:** Verás `(venv)` al inicio de tu línea de comandos cuando el entorno esté activado.

#### 5. Instalar Dependencias

Con el entorno virtual activado:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Esto instalará todas las bibliotecas necesarias (Django, Pillow, ReportLab, etc.)

#### 6. Configurar la Base de Datos

Ejecutar las migraciones para crear las tablas en la base de datos:

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 7. Crear Superusuario (Administrador)

Este será tu usuario principal para acceder al panel de administración:

```bash
python manage.py createsuperuser
```

Se te pedirá:
- **Username:** Ingresa un nombre de usuario (ej: admin)
- **Email:** Tu correo electrónico
- **Password:** Una contraseña segura (mínimo 8 caracteres)
- **Password (again):** Confirma la contraseña

> **Importante:** Guarda estas credenciales en un lugar seguro.

#### 8. Crear Directorios para Archivos Media (Opcional)

El proyecto manejará archivos subidos (imágenes de eventos, certificados, etc.). Asegúrate de que existan los directorios:

```bash
# Windows
mkdir media\eventos media\certificados media\pagos

# Linux/Mac
mkdir -p media/eventos media/certificados media/pagos
```

#### 9. Ejecutar el Servidor de Desarrollo

```bash
python manage.py runserver
```

Deberías ver un mensaje como:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

#### 10. Acceder a la Aplicación

Abre tu navegador web y ve a:

- **Página principal**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Panel de administración**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

Usa las credenciales del superusuario creadas en el paso 7 para ingresar al admin.

### Datos de Prueba (Opcional)

Si deseas cargar datos de prueba para explorar el sistema:

```bash
python create_demo_data.py
```

Esto creará:
- Eventos de ejemplo
- Usuarios de prueba
- Inscripciones simuladas
- Certificados generados

### Solución de Problemas Comunes

#### Error: "python no se reconoce como comando"
- **Solución**: Asegúrate de que Python esté en tu PATH del sistema. Reinstala Python y marca la opción "Add Python to PATH".

#### Error: "pip no se reconoce como comando"
- **Solución**: Usa `python -m pip` en lugar de solo `pip`.

#### Error: "No module named 'django'"
- **Solución**: Verifica que el entorno virtual esté activado y ejecuta `pip install -r requirements.txt` nuevamente.

#### Error al crear migraciones
- **Solución**: Ejecuta `python manage.py makemigrations` primero, luego `python manage.py migrate`.

#### Puerto 8000 ya en uso
- **Solución**: Usa otro puerto: `python manage.py runserver 8001`


## Estructura del Proyecto

```
registro_control_eventos/
├── manage.py
├── requirements.txt
├── README.md
├── .env.template
├── registro_control_eventos/          # Configuración del proyecto
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── usuarios/                          # Gestión de usuarios
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── admin.py
├── eventos/                           # Gestión de eventos
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── admin.py
├── inscripciones/                     # Gestión de inscripciones
├── asistencias/                       # Control de asistencia
├── certificados/                      # Generación de certificados
├── notificaciones/                    # Sistema de notificaciones
├── pagos/                             # Gestión de pagos
├── templates/                         # Templates HTML
│   ├── base.html
│   ├── eventos/
│   ├── usuarios/
│   └── dashboard/
├── static/                            # Archivos estáticos
│   ├── css/
│   ├── js/
│   └── images/
├── media/                             # Archivos subidos
│   ├── eventos/banners/
│   ├── certificados/
│   └── pagos/comprobantes/
└── logs/                              # Logs del sistema
```

## Configuración para Producción

### 1. Variables de Entorno

Actualizar `.env` para producción:

```env
DJANGO_ENV=production
DEBUG=False
SECRET_KEY=<GENERAR_CLAVE_SEGURA>
ALLOWED_HOSTS=tudominio.com,www.tudominio.com

# Base de datos PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=prce_db
DB_USER=prce_user
DB_PASSWORD=<PASSWORD_SEGURA>
DB_HOST=localhost
DB_PORT=5432

# Email SMTP
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=<APP_PASSWORD>

# Seguridad
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 2. Colectar Archivos Estáticos

```bash
python manage.py collectstatic --noinput
```

### 3. Configurar Servidor Web

Se recomienda usar **Gunicorn** + **Nginx**.

Instalar Gunicorn:
```bash
pip install gunicorn
```

Ejecutar:
```bash
gunicorn registro_control_eventos.wsgi:application --bind 0.0.0.0:8000
```

### 4. HTTPS

Obtener certificado SSL con Let's Encrypt:
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d tudominio.com
```

## Testing

Ejecutar tests:
```bash
pytest
```

Con cobertura:
```bash
pytest --cov=.
```

## Uso

### Acceso Inicial

1. Acceder al admin: `/admin/`
2. Crear tipos de eventos
3. Crear usuarios con roles
4. Configurar plantillas de correo
5. Crear primer evento

### Flujo de Trabajo Típico

1. **Administrador** crea evento con todos los detalles
2. **Organizador** publica el evento
3. **Asistentes** se inscriben (público o con cuenta)
4. Si tiene costo, **Asistentes** realizan pago
5. **Administrador/Organizador** confirma pagos
6. Se genera código QR automáticamente
7. Durante el evento, se registra asistencia por QR o manual
8. Al finalizar evento, sistema genera certificados automáticamente
9. Se envían certificados por correo a participantes elegibles

## Mantenimiento

### Backups

```bash
# Backup de base de datos
python manage.py dumpdata > backup.json

# Backup de archivos media
tar -czf media_backup.tar.gz media/
```

### Logs

Revisar logs en:
```
logs/django.log
```

### Actualizar Dependencias

```bash
pip list --outdated
pip install --upgrade <paquete>
pip freeze > requirements.txt
```

## Soporte

Para reportar problemas o solicitar características:

- Email: soporte@prce.com
- Issues: [GitHub Issues](URL_REPO/issues)

## Licencia

Este es un proyecto educativo para la materia de Ingeniería de Requisitos.

## Autores

- Equipo de Desarrollo - Ingeniería de Requisitos

## Agradecimientos

- Profesores y tutores del curso
- Comunidad Django
- Librerías de código abierto utilizadas

