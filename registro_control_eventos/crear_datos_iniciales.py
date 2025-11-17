"""
Script para crear datos iniciales en el sistema PRCE

Ejecutar:
python manage.py shell < crear_datos_iniciales.py
"""

from django.contrib.auth import get_user_model
from eventos.models import TipoEvento
from notificaciones.models import TipoNotificacion, PlantillaCorreo
from pagos.models import MetodoPago

Usuario = get_user_model()

print("Creando datos iniciales...")

# 1. Crear Superusuario (si no existe)
if not Usuario.objects.filter(username='admin').exists():
    admin = Usuario.objects.create_superuser(
        username='admin',
        email='admin@prce.com',
        password='admin123',
        first_name='Administrador',
        last_name='Sistema',
        documento='0000000000',
        rol='ADMINISTRADOR'
    )
    print("✓ Superusuario creado (admin/admin123)")
else:
    print("✓ Superusuario ya existe")

# 2. Crear Tipos de Evento
tipos_evento = [
    ('ACADEMICO', 'Académico', '#3498db'),
    ('CULTURAL', 'Cultural', '#9b59b6'),
    ('CORPORATIVO', 'Corporativo', '#34495e'),
    ('DEPORTIVO', 'Deportivo', '#e74c3c'),
    ('SOCIAL', 'Social', '#1abc9c'),
]

for codigo, nombre, color in tipos_evento:
    TipoEvento.objects.get_or_create(
        nombre=codigo,
        defaults={
            'descripcion': f'Eventos de tipo {nombre.lower()}',
            'color_badge': color,
            'activo': True
        }
    )
print(f"✓ {len(tipos_evento)} tipos de evento creados")

# 3. Crear Tipos de Notificación
tipos_notificacion = [
    ('CONFIRMACION_INSCRIPCION', 'Confirmación de Inscripción', True),
    ('RECORDATORIO_EVENTO', 'Recordatorio de Evento', True),
    ('CAMBIO_EVENTO', 'Cambio en Evento', True),
    ('CANCELACION_EVENTO', 'Cancelación de Evento', True),
    ('CERTIFICADO_DISPONIBLE', 'Certificado Disponible', True),
    ('PAGO_CONFIRMADO', 'Confirmación de Pago', True),
    ('INSCRIPCION_APROBADA', 'Inscripción Aprobada', True),
    ('INSCRIPCION_RECHAZADA', 'Inscripción Rechazada', True),
]

for codigo, nombre, activo in tipos_notificacion:
    TipoNotificacion.objects.get_or_create(
        codigo=codigo,
        defaults={
            'nombre': nombre,
            'descripcion': f'Notificación de {nombre.lower()}',
            'activo': activo
        }
    )
print(f"✓ {len(tipos_notificacion)} tipos de notificación creados")

# 4. Crear Plantilla de Confirmación de Inscripción
tipo_confirmacion = TipoNotificacion.objects.get(codigo='CONFIRMACION_INSCRIPCION')
PlantillaCorreo.objects.get_or_create(
    tipo_notificacion=tipo_confirmacion,
    nombre='Confirmación de Inscripción - Predeterminada',
    defaults={
        'asunto': 'Confirmación de inscripción - {{evento}}',
        'cuerpo_texto': '''
Estimado/a {{nombre}},

Su inscripción al evento "{{evento}}" ha sido confirmada exitosamente.

Detalles del evento:
- Fecha: {{fecha}}
- Hora: {{hora}}
- Lugar: {{lugar}}

Adjunto encontrará su código QR para registro de asistencia.

Saludos cordiales,
Equipo PRCE
        ''',
        'pie_pagina': 'Este es un correo automático, por favor no responda.',
        'activa': True,
        'predeterminada': True,
        'variables_disponibles': '{{nombre}}, {{evento}}, {{fecha}}, {{hora}}, {{lugar}}, {{codigo_qr}}'
    }
)
print("✓ Plantilla de confirmación creada")

# 5. Crear Métodos de Pago
metodos_pago = [
    ('EFECTIVO', 'Efectivo', False),
    ('TRANSFERENCIA', 'Transferencia Bancaria', True),
    ('TARJETA', 'Tarjeta de Crédito/Débito', False),
    ('PASARELA', 'Pasarela de Pagos', False),
]

for codigo, nombre, requiere_comprobante in metodos_pago:
    MetodoPago.objects.get_or_create(
        codigo=codigo,
        defaults={
            'nombre': nombre,
            'descripcion': f'Pago mediante {nombre.lower()}',
            'activo': True,
            'requiere_comprobante': requiere_comprobante
        }
    )
print(f"✓ {len(metodos_pago)} métodos de pago creados")

print("\n¡Datos iniciales creados exitosamente!")
print("\nPuedes iniciar sesión con:")
print("Usuario: admin")
print("Contraseña: admin123")

