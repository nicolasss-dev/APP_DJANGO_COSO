# Guía de Contribución

## Bienvenido

Gracias por tu interés en contribuir a la **Plataforma de Registro y Control de Eventos (PRCE)**. Esta guía te ayudará a empezar.

## Código de Conducta

- Sé respetuoso y profesional
- Acepta críticas constructivas
- Enfócate en lo mejor para el proyecto

## Cómo Contribuir

### 1. Reportar Bugs

Si encuentras un bug, abre un issue con:
- Descripción clara del problema
- Pasos para reproducirlo
- Comportamiento esperado vs actual
- Screenshots si aplica
- Versión de Python y Django

### 2. Proponer Features

Para proponer nuevas funcionalidades:
- Abre un issue describiendo la funcionalidad
- Explica el caso de uso y beneficios
- Espera feedback antes de iniciar el desarrollo

### 3. Enviar Pull Requests

#### Preparación del Entorno

```bash
# Clonar el repositorio
git clone https://github.com/nicolasss-dev/APP_DJANGO_COSO.git
cd APP_DJANGO_COSO/registro_control_eventos

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

#### Flujo de Trabajo

1. **Fork** el repositorio
2. **Crea una rama** para tu feature:
   ```bash
   git checkout -b feature/nombre-descriptivo
   ```
3. **Haz commits** siguiendo las convenciones:
   ```
   feat: Añade registro de asistencias por QR
   fix: Corrige error en generación de certificados
   docs: Actualiza documentación de API
   test: Añade tests para modelo Evento
   refactor: Mejora estructura de carpetas
   ```
4. **Ejecuta tests**:
   ```bash
   python manage.py test
   # o con pytest
   pytest
   ```
5. **Push** a tu fork:
   ```bash
   git push origin feature/nombre-descriptivo
   ```
6. **Abre un Pull Request** al branch `main`

### Estándares de Código

#### Python/Django
- Sigue PEP 8
- Usa nombres descriptivos en inglés para variables y funciones
- Documenta funciones complejas con docstrings
- Máximo 100 caracteres por línea

#### Testing
- Escribe tests para nuevo código
- Mantén cobertura > 80%
- Usa docstrings descriptivos en tests

#### Commits
- Usa commits atómicos (un cambio lógico por commit)
- Mensajes en español, claros y descriptivos
- Referencia issues cuando aplique (#123)

### Estructura del Proyecto

```
registro_control_eventos/
├── eventos/           # Gestión de eventos
├── usuarios/          # Autenticación y usuarios
├── inscripciones/     # Registro de participantes
├── asistencias/       # Control de asistencia
├── certificados/      # Generación de certificados
├── notificaciones/    # Sistema de emails
├── pagos/             # Gestión de pagos
├── reportes/          # Reportes y estadísticas
├── templates/         # Templates HTML
└── static/            # CSS, JS, imágenes
```

### Testing

```bash
# Ejecutar todos los tests
python manage.py test

# Tests específicos
python manage.py test eventos.tests

# Con pytest
pytest
pytest -v  # verbose
pytest --cov  # con cobertura
```

### Migrations

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Ver SQL generado
python manage.py sqlmigrate eventos 0001
```

## Preguntas

Si tienes dudas, abre un issue con la etiqueta `question`.

## Licencia

Al contribuir, aceptas que tu código se distribuya bajo la misma licencia del proyecto.
