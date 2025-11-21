# Guía de Instalación Rápida
# Plataforma Web de Registro y Control de Eventos (PRCE)

## ¿Primera vez? Sigue estos pasos:

### 1. Requisitos Previos
- Python 3.12+ instalado
- Git instalado

### 2. Clonar el Proyecto
```bash
git clone <url_del_repositorio>
cd registro_control_eventos
```

### 3. Crear y Activar Entorno Virtual
```bash
# Crear
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (Linux/Mac)
source venv/bin/activate
```

### 4. Instalar Dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configurar Base de Datos
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear Usuario Administrador
```bash
python manage.py createsuperuser
```

### 7. Ejecutar Servidor
```bash
python manage.py runserver
```

### 8. Acceder
- App: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## Datos de Prueba (Opcional)
```bash
python create_demo_data.py
```

---

Para más detalles, consulta el archivo `README.md` completo.
