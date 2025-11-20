#!/usr/bin/env python
"""
Script para ejecutar tests del proyecto PRCE
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(__file__))

# Configurar Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'registro_control_eventos.settings')

import django
django.setup()

# Ejecutar tests
if __name__ == '__main__':
    from django.core.management import call_command
    
    print("=" * 60)
    print("PRCE - Ejecutando Tests")
    print("=" * 60)
    print()
    
    # Opción 1: Usar pytest si está disponible
    try:
        import pytest
        sys.exit(pytest.main([
            '-v',
            '--tb=short',
            '--ds=registro_control_eventos.settings',
        ]))
    except ImportError:
        # Opción 2: Usar el sistema de tests de Django
        print("Pytest no disponible. Usando sistema de tests de Django...")
        call_command('test', verbosity=2)

