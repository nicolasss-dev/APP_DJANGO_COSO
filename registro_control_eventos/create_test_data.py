import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'registro_control_eventos.settings')
django.setup()

from usuarios.models import Usuario
from eventos.models import Evento, TipoEvento
from inscripciones.models import Inscripcion
from asistencias.models import Asistencia

def create_test_data():
    print("Creating test data...")
    
    # Create user
    user, created = Usuario.objects.get_or_create(
        email='testuser@example.com',
        defaults={
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True
        }
    )
    if created:
        user.set_password('password123')
        user.save()
        print(f"User created: {user.email}")
    else:
        print(f"User already exists: {user.email}")

    # Create admin user for managing events
    admin, created = Usuario.objects.get_or_create(
        email='admin@example.com',
        defaults={
            'username': 'admin',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print(f"Admin created: {admin.email}")
    
    # Create event type
    tipo, _ = TipoEvento.objects.get_or_create(nombre='ACADEMICO')
    
    # Create event
    evento, created = Evento.objects.get_or_create(
        nombre='Curso de Python Avanzado',
        defaults={
            'descripcion': 'Curso avanzado de programación en Python',
            'tipo_evento': tipo,
            'fecha_inicio': timezone.now() - timedelta(days=5),
            'fecha_fin': timezone.now() + timedelta(days=5),
            'lugar': 'Virtual',
            'cupo_maximo': 50,
            'costo': 0,
            'estado': 'PUBLICADO',
            'creado_por': admin,
            'numero_sesiones': 5,
            'porcentaje_asistencia_minimo': 80,
            'genera_certificado': True
        }
    )
    print(f"Event created/retrieved: {evento.nombre}")
    
    # Register user
    inscripcion, created = Inscripcion.objects.get_or_create(
        evento=evento,
        usuario=user,
        defaults={
            'nombre': user.first_name,
            'apellido': user.last_name,
            'documento': '123456789',
            'correo': user.email,
            'telefono': '555-1234',
            'estado': 'CONFIRMADA',
            'pago_confirmado': True
        }
    )
    print(f"Registration created/retrieved: {inscripcion}")
    
    # Create attendance records (4 out of 5 sessions = 80%)
    for i in range(1, 5):
        Asistencia.objects.get_or_create(
            inscripcion=inscripcion,
            sesion=i,
            defaults={
                'metodo_registro': 'MANUAL',
                'registrado_por': admin
            }
        )
    print("Attendance records created")
    
    return evento.id, user.id

if __name__ == '__main__':
    create_test_data()
