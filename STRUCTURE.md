# Estructura del Proyecto
# Plataforma Web de Registro y Control de Eventos (PRCE)

## Contenido del Repositorio

```
APP_DJANGO_COSO/
│
├── .gitignore                                  # Archivos ignorados por Git
├── .gitattributes                              # Configuración de atributos de Git
├── INSTALL.md                                  # Guía de instalación rápida
│
└── registro_control_eventos/                   # Directorio principal del proyecto
    ├── manage.py                               # Script de gestión de Django
    ├── README.md                               # Documentación completa
    ├── requirements.txt                        # Dependencias del proyecto
    │
    ├── registro_control_eventos/               # Configuración del proyecto Django
    │   ├── __init__.py
    │   ├── settings.py                         # Configuración principal
    │   ├── urls.py                             # Rutas principales
    │   ├── wsgi.py                             # Punto de entrada WSGI
    │   └── asgi.py                             # Punto de entrada ASGI
    │
    ├── usuarios/                               # App: Gestión de usuarios
    │   ├── models.py                           # Modelo CustomUser con roles
    │   ├── views.py                            # Vistas de autenticación y perfiles
    │   ├── forms.py                            # Formularios de registro y perfil
    │   ├── admin.py                            # Configuración del admin
    │   └── urls.py                             # Rutas de usuarios
    │
    ├── eventos/                                # App: Gestión de eventos
    │   ├── models.py                           # Modelo Evento y TipoEvento
    │   ├── views.py                            # CRUD de eventos
    │   ├── forms.py                            # Formularios de eventos
    │   └── admin.py                            # Admin de eventos
    │
    ├── inscripciones/                          # App: Gestión de inscripciones
    │   ├── models.py                           # Modelo Inscripcion
    │   ├── views.py                            # Registro público y gestión
    │   ├── forms.py                            # Formularios de inscripción
    │   └── utils.py                            # Generación de códigos QR
    │
    ├── asistencias/                            # App: Control de asistencia
    │   ├── models.py                           # Modelo Asistencia
    │   ├── views.py                            # Registro de asistencia
    │   └── admin.py                            # Admin de asistencia
    │
    ├── certificados/                           # App: Generación de certificados
    │   ├── models.py                           # Modelo Certificado y PlantillaCertificado
    │   ├── views.py                            # Generación y descarga de PDFs
    │   └── utils.py                            # Lógica de generación con ReportLab
    │
    ├── notificaciones/                         # App: Sistema de notificaciones
    │   ├── models.py                           # Modelos de plantillas y recordatorios
    │   ├── views.py                            # Gestión de notificaciones
    │   ├── tasks.py                            # Tareas de envío de correos
    │   └── admin.py                            # Admin de notificaciones
    │
    ├── pagos/                                  # App: Gestión de pagos
    │   ├── models.py                           # Modelo Pago y MetodoPago
    │   ├── views.py                            # Registro y confirmación de pagos
    │   ├── forms.py                            # Formularios de pago
    │   └── admin.py                            # Admin de pagos
    │
    ├── reportes/                               # App: Reportes y estadísticas
    │   ├── views.py                            # Generación de reportes
    │   └── urls.py                             # Rutas de reportes
    │
    ├── dashboard/                              # App: Panel de control
    │   ├── views.py                            # Dashboard principal
    │   └── urls.py                             # Rutas del dashboard
    │
    ├── templates/                              # Templates HTML del proyecto
    │   ├── base.html                           # Template base
    │   ├── usuarios/                           # Templates de usuarios
    │   ├── eventos/                            # Templates de eventos
    │   ├── inscripciones/                      # Templates de inscripciones
    │   ├── asistencias/                        # Templates de asistencia
    │   ├── certificados/                       # Templates de certificados
    │   ├── notificaciones/                     # Templates de notificaciones
    │   ├── pagos/                              # Templates de pagos
    │   ├── reportes/                           # Templates de reportes
    │   └── dashboard/                          # Templates del dashboard
    │
    ├── static/                                 # Archivos estáticos (CSS, JS, imágenes)
    │   ├── css/
    │   ├── js/
    │   └── images/
    │
    ├── media/                                  # Archivos subidos por usuarios (ignorado en Git)
    │   ├── eventos/                            # Banners de eventos
    │   ├── certificados/                       # PDFs de certificados
    │   └── pagos/                              # Comprobantes de pago
    │
    └── logs/                                   # Logs del sistema (ignorado en Git)
        └── django.log
```

## Archivos NO Incluidos en el Repositorio

Por seguridad y buenas prácticas, los siguientes archivos/directorios **NO** están en Git:

- `__pycache__/` - Bytecode compilado de Python
- `*.pyc`, `*.pyo` - Archivos compilados
- `venv/`, `env/` - Entorno virtual
- `db.sqlite3` - Base de datos de desarrollo (cada usuario crea la suya)
- `.env` - Variables de entorno sensibles
- `media/` - Archivos subidos (certificados, comprobantes, fotos)
- `staticfiles/` - Archivos estáticos recolectados
- `logs/` - Archivos de log
- `.cursor/`, `.vscode/`, `.idea/` - Configuraciones del IDE

Estos archivos se generarán automáticamente al ejecutar la instalación.

## Apps del Proyecto

| App | Responsabilidad |
|-----|-----------------|
| `usuarios` | Autenticación, registro, perfiles, roles |
| `eventos` | Crear, editar, listar eventos |
| `inscripciones` | Registro de asistentes, códigos QR |
| `asistencias` | Control de asistencia por evento/sesión |
| `certificados` | Generación automática de PDFs |
| `notificaciones` | Envío de correos y recordatorios |
| `pagos` | Registro y gestión de pagos |
| `reportes` | Generación de reportes y estadísticas |
| `dashboard` | Panel principal de administración |

## Modelos Principales

- **CustomUser**: Usuarios con roles (Admin, Organizador, Asistente)
- **Evento**: Eventos con tipo, fechas, capacidad, precio
- **Inscripcion**: Relación usuario-evento con código QR
- **Asistencia**: Registro de asistencia por sesión
- **Certificado**: PDF generado con código de verificación
- **Pago**: Registro de transacciones
- **PlantillaNotificacion**: Templates de correos configurables

## URLs Principales

- `/` - Página de inicio
- `/admin/` - Panel de administración de Django
- `/dashboard/` - Dashboard del sistema
- `/eventos/` - Listado de eventos
- `/eventos/crear/` - Crear nuevo evento
- `/eventos/<id>/` - Detalle de evento
- `/inscripciones/` - Mis inscripciones
- `/inscripciones/evento/<id>/` - Registro público
- `/asistencias/evento/<id>/` - Control de asistencia
- `/certificados/` - Mis certificados
- `/pagos/` - Mis pagos
- `/reportes/` - Reportes y estadísticas
- `/usuarios/perfil/` - Mi perfil
- `/usuarios/login/` - Inicio de sesión
- `/usuarios/registro/` - Registro de cuenta

## Tecnologías y Versiones

- Python: 3.12+
- Django: 5.2.8
- Base de datos desarrollo: SQLite3
- Base de datos producción: PostgreSQL (recomendado)
- ReportLab: Generación de PDFs
- qrcode: Generación de códigos QR
- Bootstrap: Framework CSS
- Font Awesome: Iconos

Para más detalles de instalación y configuración, consulta `README.md` e `INSTALL.md`.
