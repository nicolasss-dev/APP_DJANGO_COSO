#!/usr/bin/env python
"""
Script de Verificación del Sistema PRCE
Verifica que todos los componentes estén correctamente configurados
"""

import os
import sys
from pathlib import Path

# Colores para la consola
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_ok(msg):
    print(f"{Colors.GREEN}[OK] {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}[ERROR] {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}[INFO] {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}[WARN] {msg}{Colors.END}")

def verificar_estructura_directorios():
    """Verificar que existan todos los directorios necesarios"""
    print("\n[1/7] Verificando Estructura de Directorios...")
    
    directorios = [
        'templates',
        'templates/usuarios',
        'templates/eventos',
        'templates/dashboard',
        'templates/inscripciones',
        'templates/asistencias',
        'templates/certificados',
        'templates/pagos',
        'templates/reportes',
        'static',
        'static/css',
        'static/js',
        'media',
        'logs',
    ]
    
    todos_ok = True
    for directorio in directorios:
        path = Path(directorio)
        if path.exists():
            print_ok(f"Directorio existe: {directorio}")
        else:
            print_error(f"Directorio faltante: {directorio}")
            todos_ok = False
    
    return todos_ok

def verificar_templates():
    """Verificar que existan todos los templates necesarios"""
    print("\n[2/7] Verificando Templates...")
    
    templates = [
        'templates/base.html',
        'templates/dashboard/index.html',
        'templates/usuarios/login.html',
        'templates/usuarios/perfil.html',
        'templates/usuarios/lista.html',
        'templates/usuarios/crear.html',
        'templates/usuarios/editar.html',
        'templates/eventos/lista.html',
        'templates/eventos/crear.html',
        'templates/eventos/editar.html',
        'templates/eventos/detalle.html',
        'templates/eventos/eliminar_confirmar.html',
        'templates/inscripciones/lista.html',
        'templates/asistencias/lista.html',
        'templates/certificados/lista.html',
        'templates/pagos/lista.html',
        'templates/reportes/dashboard.html',
    ]
    
    todos_ok = True
    for template in templates:
        path = Path(template)
        if path.exists():
            print_ok(f"Template existe: {template}")
        else:
            print_error(f"Template faltante: {template}")
            todos_ok = False
    
    return todos_ok

def verificar_archivos_python():
    """Verificar archivos Python importantes"""
    print("\n[3/7] Verificando Archivos Python...")
    
    archivos = [
        'manage.py',
        'registro_control_eventos/settings.py',
        'registro_control_eventos/urls.py',
        'usuarios/models.py',
        'usuarios/views.py',
        'usuarios/forms.py',
        'usuarios/urls.py',
        'eventos/models.py',
        'eventos/views.py',
        'eventos/forms.py',
        'eventos/urls.py',
        'dashboard/views.py',
    ]
    
    todos_ok = True
    for archivo in archivos:
        path = Path(archivo)
        if path.exists():
            print_ok(f"Archivo existe: {archivo}")
        else:
            print_error(f"Archivo faltante: {archivo}")
            todos_ok = False
    
    return todos_ok

def verificar_base_datos():
    """Verificar que exista la base de datos"""
    print("\n[4/7] Verificando Base de Datos...")
    
    if Path('db.sqlite3').exists():
        print_ok("Base de datos existe (db.sqlite3)")
        return True
    else:
        print_warning("Base de datos no existe - ejecute: python manage.py migrate")
        return False

def verificar_dependencias():
    """Verificar dependencias instaladas"""
    print("\n[5/7] Verificando Dependencias...")
    
    try:
        import django
        print_ok(f"Django instalado: versión {django.get_version()}")
    except ImportError:
        print_error("Django no está instalado")
        return False
    
    dependencias = [
        'reportlab',
        'PIL',
        'qrcode',
        'openpyxl',
        'pandas',
        'dotenv',
        'pytest',
    ]
    
    todos_ok = True
    for dep in dependencias:
        try:
            __import__(dep)
            print_ok(f"Dependencia instalada: {dep}")
        except ImportError:
            print_warning(f"Dependencia opcional no instalada: {dep}")
    
    return todos_ok

def verificar_configuracion():
    """Verificar configuración de Django"""
    print("\n[6/7] Verificando Configuracion de Django...")
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'registro_control_eventos.settings')
    
    try:
        import django
        django.setup()
        
        from django.conf import settings
        
        # Verificar configuraciones clave
        print_ok("Django configurado correctamente")
        print_info(f"DEBUG = {settings.DEBUG}")
        print_info(f"ALLOWED_HOSTS = {settings.ALLOWED_HOSTS}")
        print_info(f"DATABASES = {settings.DATABASES['default']['ENGINE']}")
        
        return True
    except Exception as e:
        print_error(f"Error en configuración: {e}")
        return False

def verificar_modelos():
    """Verificar que los modelos estén correctamente configurados"""
    print("\n[7/7] Verificando Modelos de Base de Datos...")
    
    try:
        from usuarios.models import Usuario
        from eventos.models import Evento, TipoEvento
        from inscripciones.models import Inscripcion
        
        print_ok("Modelo Usuario importado correctamente")
        print_ok("Modelo Evento importado correctamente")
        print_ok("Modelo TipoEvento importado correctamente")
        print_ok("Modelo Inscripcion importado correctamente")
        
        # Verificar conteos
        print_info(f"Usuarios en BD: {Usuario.objects.count()}")
        print_info(f"Eventos en BD: {Evento.objects.count()}")
        print_info(f"Tipos de Evento en BD: {TipoEvento.objects.count()}")
        
        return True
    except Exception as e:
        print_error(f"Error al verificar modelos: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 70)
    print("VERIFICACION DEL SISTEMA PRCE")
    print("=" * 70)
    
    resultados = []
    
    # Ejecutar verificaciones
    resultados.append(("Estructura de Directorios", verificar_estructura_directorios()))
    resultados.append(("Templates", verificar_templates()))
    resultados.append(("Archivos Python", verificar_archivos_python()))
    resultados.append(("Base de Datos", verificar_base_datos()))
    resultados.append(("Dependencias", verificar_dependencias()))
    resultados.append(("Configuración Django", verificar_configuracion()))
    resultados.append(("Modelos", verificar_modelos()))
    
    # Resumen
    print("\n" + "=" * 70)
    print("RESUMEN DE VERIFICACION")
    print("=" * 70)
    
    total = len(resultados)
    exitosos = sum(1 for _, resultado in resultados if resultado)
    
    for nombre, resultado in resultados:
        if resultado:
            print_ok(f"{nombre}: OK")
        else:
            print_error(f"{nombre}: FALLO")
    
    print("\n" + "=" * 70)
    if exitosos == total:
        print_ok(f"TODAS LAS VERIFICACIONES PASARON ({exitosos}/{total})")
        print_info("El sistema esta listo para usar!")
        print_info("Ejecute: python manage.py runserver")
    else:
        print_warning(f"ALGUNAS VERIFICACIONES FALLARON ({exitosos}/{total})")
        print_info("Revise los errores anteriores y corrija los problemas.")
    print("=" * 70)

if __name__ == '__main__':
    main()

