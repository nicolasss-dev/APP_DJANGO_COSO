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

## Instalación

### Prerrequisitos

- Python 3.12 o superior
- pip (gestor de paquetes de Python)
- Git

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <URL_DEL_REPOSITORIO>
cd DJANGO_FINAL_TEMPLATE/registro_control_eventos
```

2. **Crear entorno virtual**
```bash
python -m venv venv
```

3. **Activar entorno virtual**

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

4. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

5. **Configurar variables de entorno**

Copiar `.env.template` a `.env` y configurar:
```bash
cp .env.template .env
```

Editar `.env` con tus configuraciones.

6. **Ejecutar migraciones**
```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Crear superusuario**
```bash
python manage.py createsuperuser
```

8. **Cargar datos iniciales (opcional)**
```bash
python manage.py loaddata fixtures/initial_data.json
```

9. **Ejecutar servidor de desarrollo**
```bash
python manage.py runserver
```

10. **Acceder a la aplicación**
```
http://127.0.0.1:8000/
```

Admin: http://127.0.0.1:8000/admin/

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

