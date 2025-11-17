# 🚀 Guía de Inicio Rápido - PRCE

## Plataforma de Registro y Control de Eventos

Esta guía te ayudará a poner en marcha el sistema en menos de 5 minutos.

## 📋 Requisitos Previos

- Python 3.12 o superior
- pip (gestor de paquetes de Python)
- Git (opcional)

## ⚡ Instalación Rápida

### 1. Clonar o Descargar el Proyecto

```bash
cd DJANGO_FINAL_TEMPLATE/registro_control_eventos
```

### 2. Crear Entorno Virtual

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

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
copy .env.example .env  # Windows
# o
cp .env.example .env    # Linux/Mac
```

> **Nota:** Para desarrollo, los valores por defecto en `.env.example` son suficientes.

### 5. Aplicar Migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear Superusuario

```bash
python manage.py createsuperuser
```

Datos sugeridos:
- **Usuario:** admin
- **Email:** admin@prce.com
- **Contraseña:** admin123 (cambiar en producción)

### 7. Cargar Datos Iniciales (Opcional)

```bash
python manage.py shell < crear_datos_iniciales.py
```

### 8. Iniciar Servidor

```bash
python manage.py runserver
```

## 🌐 Acceder al Sistema

- **Aplicación principal:** http://127.0.0.1:8000/
- **Panel de administración:** http://127.0.0.1:8000/admin/
- **Login:** http://127.0.0.1:8000/usuarios/login/

## 👥 Usuarios de Ejemplo

Si cargaste los datos iniciales, puedes usar:

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| admin | admin123 | Administrador |
| organizador1 | org123 | Organizador |
| asistente1 | asis123 | Asistente |

## 📚 Módulos Disponibles

✅ **Gestión de Usuarios** - Crear, editar, asignar roles
✅ **Gestión de Eventos** - CRUD completo, duplicar, publicar
✅ **Inscripciones** - Registro público y masivo
✅ **Control de Asistencia** - Manual y por QR
✅ **Certificados** - Generación automática de PDFs
✅ **Notificaciones** - Correos configurables
✅ **Pagos** - Registro manual y reportes
✅ **Dashboard** - Estadísticas y KPIs
✅ **Reportes** - Exportación a PDF y Excel

## 🔧 Configuración Adicional

### Envío de Correos (Opcional)

Para activar el envío real de correos, edita `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password
```

### Base de Datos PostgreSQL (Producción)

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=prce_db
DB_USER=prce_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432
```

## 🐛 Solución de Problemas

### Error de migraciones

```bash
python manage.py migrate --run-syncdb
```

### Problemas con dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Puerto 8000 en uso

```bash
python manage.py runserver 8080
```

## 📖 Documentación Completa

Para más detalles, consulta:
- `README.md` - Documentación completa del proyecto
- `INSTALL.md` - Guía detallada de instalación
- `PROYECTO_COMPLETADO.md` - Resumen de funcionalidades

## 🆘 Soporte

Para reportar problemas o solicitar ayuda:
- Revisa la documentación en el repositorio
- Consulta las historias de usuario implementadas
- Contacta al equipo de desarrollo

---

**¡Listo!** Tu sistema PRCE está funcionando. 🎉

¿Próximos pasos?
1. Explora el panel de administración
2. Crea tu primer evento
3. Configura las plantillas de correo
4. Personaliza los colores y estilos

