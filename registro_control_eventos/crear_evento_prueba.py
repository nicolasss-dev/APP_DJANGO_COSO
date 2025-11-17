"""
Script para crear eventos de prueba en el sistema
Ejecutar: python manage.py shell < crear_evento_prueba.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'registro_control_eventos.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from eventos.models import Evento, TipoEvento
from usuarios.models import Usuario

print("=" * 70)
print("CREANDO EVENTOS DE PRUEBA")
print("=" * 70)

# Obtener o crear usuario admin
try:
    admin = Usuario.objects.get(username='admin')
    print(f"✓ Usuario admin encontrado: {admin.email}")
except Usuario.DoesNotExist:
    admin = Usuario.objects.create_superuser(
        username='admin',
        email='admin@prce.com',
        password='admin123',
        first_name='Administrador',
        last_name='Sistema',
        documento='0000000000',
        rol='ADMINISTRADOR'
    )
    print("✓ Usuario admin creado")

# Verificar que existan tipos de evento
tipos = TipoEvento.objects.all()
if tipos.count() == 0:
    print("✗ No hay tipos de evento. Ejecute: python -c \"import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'registro_control_eventos.settings'); import django; django.setup(); exec(open('crear_datos_iniciales.py').read())\"")
    exit(1)

print(f"✓ Tipos de evento disponibles: {tipos.count()}")

# Crear eventos de prueba
eventos_prueba = [
    {
        'nombre': 'Taller de Python para Principiantes',
        'descripcion': 'Aprende los fundamentos de Python desde cero. Incluye ejemplos prácticos y ejercicios.',
        'tipo': 'ACADEMICO',
        'dias_futuro': 7,
        'duracion_horas': 3,
        'lugar': 'Aula de Informática 101',
        'cupo': 30,
        'costo': Decimal('0.00'),
    },
    {
        'nombre': 'Concierto de Música Clásica',
        'descripcion': 'Presentación de la Orquesta Sinfónica con obras de Mozart, Beethoven y Tchaikovsky.',
        'tipo': 'CULTURAL',
        'dias_futuro': 14,
        'duracion_horas': 2,
        'lugar': 'Teatro Municipal',
        'cupo': 200,
        'costo': Decimal('25000.00'),
    },
    {
        'nombre': 'Feria de Emprendimiento',
        'descripcion': 'Espacio para emprendedores locales. Networking, charlas y exhibición de productos.',
        'tipo': 'CORPORATIVO',
        'dias_futuro': 21,
        'duracion_horas': 6,
        'lugar': 'Centro de Convenciones',
        'cupo': 150,
        'costo': Decimal('0.00'),
    },
    {
        'nombre': 'Maratón Universitaria 5K',
        'descripcion': 'Carrera recreativa de 5 kilómetros. Incluye hidratación y camiseta conmemorativa.',
        'tipo': 'DEPORTIVO',
        'dias_futuro': 28,
        'duracion_horas': 4,
        'lugar': 'Parque Central',
        'cupo': 500,
        'costo': Decimal('15000.00'),
    },
    {
        'nombre': 'Fiesta de Integración Estudiantil',
        'descripcion': 'Evento social para estudiantes nuevos. DJ en vivo, comida y actividades recreativas.',
        'tipo': 'SOCIAL',
        'dias_futuro': 10,
        'duracion_horas': 5,
        'lugar': 'Salón de Eventos Universidad',
        'cupo': 250,
        'costo': Decimal('20000.00'),
    },
]

eventos_creados = 0
for evento_data in eventos_prueba:
    # Verificar si ya existe
    if Evento.objects.filter(nombre=evento_data['nombre']).exists():
        print(f"○ Ya existe: {evento_data['nombre']}")
        continue
    
    # Obtener tipo de evento
    try:
        tipo_evento = TipoEvento.objects.get(nombre=evento_data['tipo'])
    except TipoEvento.DoesNotExist:
        print(f"✗ Tipo no encontrado: {evento_data['tipo']}")
        continue
    
    # Calcular fechas
    fecha_inicio = timezone.now() + timedelta(days=evento_data['dias_futuro'])
    fecha_fin = fecha_inicio + timedelta(hours=evento_data['duracion_horas'])
    
    # Crear evento
    evento = Evento.objects.create(
        nombre=evento_data['nombre'],
        descripcion=evento_data['descripcion'],
        tipo_evento=tipo_evento,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        lugar=evento_data['lugar'],
        cupo_maximo=evento_data['cupo'],
        costo=evento_data['costo'],
        estado='PUBLICADO',  # Importante: PUBLICADO para que aparezca
        creado_por=admin,
        genera_certificado=True,
        porcentaje_asistencia_minimo=80,
        numero_sesiones=1
    )
    
    print(f"✓ Creado: {evento.nombre}")
    print(f"  - Fecha: {evento.fecha_inicio.strftime('%d/%m/%Y %H:%M')}")
    print(f"  - Tipo: {evento.tipo_evento}")
    print(f"  - Costo: {'GRATUITO' if evento.es_gratuito else f'${evento.costo}'}")
    print(f"  - Cupos: {evento.cupo_maximo}")
    print(f"  - Estado: {evento.estado}")
    eventos_creados += 1

print("\n" + "=" * 70)
print(f"RESUMEN: {eventos_creados} eventos nuevos creados")
print("=" * 70)

# Mostrar estadísticas
total_eventos = Evento.objects.filter(estado='PUBLICADO').count()
eventos_futuros = Evento.objects.filter(
    estado='PUBLICADO',
    fecha_inicio__gte=timezone.now()
).count()

print(f"\nEstadísticas actuales:")
print(f"  Total eventos PUBLICADOS: {total_eventos}")
print(f"  Eventos futuros disponibles: {eventos_futuros}")
print(f"  Tipos de evento: {TipoEvento.objects.count()}")

print("\n" + "=" * 70)
print("URLs para verificar:")
print("  Dashboard: http://localhost:8000/dashboard/")
print("  Eventos disponibles: http://localhost:8000/inscripciones/registro-publico/")
print("  Lista de eventos: http://localhost:8000/eventos/")
print("=" * 70)

