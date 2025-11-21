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
from certificados.models import Certificado

def create_demo_data():
    print("Creating demo data...")
    
    # Ensure admin exists
    admin, _ = Usuario.objects.get_or_create(
        email='admin@example.com',
        defaults={'username': 'admin', 'is_staff': True, 'is_superuser': True}
    )
    if not admin.check_password('admin123'):
        admin.set_password('admin123')
        admin.save()

    # Ensure demo users exist
    users = []
    for i, name in enumerate(['Alice', 'Bob', 'Charlie']):
        email = f'{name.lower()}@example.com'
        documento = f'DEMO{i+1:05d}'
        
        # Try to get user by email
        try:
            user = Usuario.objects.get(email=email)
            # Update document if missing
            if not user.documento:
                user.documento = documento
                user.save()
        except Usuario.DoesNotExist:
            user = Usuario.objects.create_user(
                username=name.lower(),
                email=email,
                password='password123',
                first_name=name,
                last_name='Demo',
                documento=documento,
                rol='ASISTENTE'
            )
            
        users.append(user)
    
    alice, bob, charlie = users

    # --- Scenario 1: Automatic Certificate Generation ---
    print("\n--- Scenario 1: Automatic Certificates ---")
    tipo_acad, _ = TipoEvento.objects.get_or_create(nombre='ACADEMICO')
    
    evento_cert, _ = Evento.objects.get_or_create(
        nombre='Taller de Certificación Automática',
        defaults={
            'descripcion': 'Este evento genera certificados automáticamente al cumplir 100% de asistencia.',
            'tipo_evento': tipo_acad,
            'fecha_inicio': timezone.now() - timedelta(days=10),
            'fecha_fin': timezone.now() - timedelta(days=8),
            'lugar': 'Sala A',
            'cupo_maximo': 20,
            'costo': 0,
            'estado': 'FINALIZADO',
            'creado_por': admin,
            'numero_sesiones': 3,
            'porcentaje_asistencia_minimo': 100,
            'genera_certificado': True
        }
    )
    
    # Register Alice and give her 100% attendance
    insc_alice, _ = Inscripcion.objects.get_or_create(
        evento=evento_cert,
        usuario=alice,
        defaults={'estado': 'CONFIRMADA', 'pago_confirmado': True}
    )
    
    for i in range(1, 4):
        Asistencia.objects.get_or_create(
            inscripcion=insc_alice,
            sesion=i,
            defaults={'metodo_registro': 'MANUAL', 'registrado_por': admin}
        )
        
    # Simulate automatic generation
    print(f"Generating certificates for {evento_cert.nombre}...")
    generated = Certificado.generar_certificados_evento(evento_cert)
    print(f"Generated {len(generated)} certificates.")
    
    # --- Scenario 2: Attendance Report ---
    print("\n--- Scenario 2: Attendance Report ---")
    evento_reporte, _ = Evento.objects.get_or_create(
        nombre='Seminario de Análisis de Datos',
        defaults={
            'descripcion': 'Evento con múltiples participantes para visualizar el reporte de asistencia.',
            'tipo_evento': tipo_acad,
            'fecha_inicio': timezone.now() - timedelta(days=5),
            'fecha_fin': timezone.now() - timedelta(days=1),
            'lugar': 'Auditorio Principal',
            'cupo_maximo': 50,
            'costo': 0,
            'estado': 'EN_CURSO',
            'creado_por': admin,
            'numero_sesiones': 4,
            'porcentaje_asistencia_minimo': 75,
            'genera_certificado': True
        }
    )
    
    # Alice: 100% (4/4)
    i_alice, _ = Inscripcion.objects.get_or_create(evento=evento_reporte, usuario=alice, defaults={'estado': 'CONFIRMADA'})
    for i in range(1, 5):
        Asistencia.objects.get_or_create(inscripcion=i_alice, sesion=i, defaults={'metodo_registro': 'MANUAL'})

    # Bob: 50% (2/4)
    i_bob, _ = Inscripcion.objects.get_or_create(evento=evento_reporte, usuario=bob, defaults={'estado': 'CONFIRMADA'})
    for i in range(1, 3):
        Asistencia.objects.get_or_create(inscripcion=i_bob, sesion=i, defaults={'metodo_registro': 'MANUAL'})

    # Charlie: 0% (0/4)
    i_charlie, _ = Inscripcion.objects.get_or_create(evento=evento_reporte, usuario=charlie, defaults={'estado': 'CONFIRMADA'})
    
    print(f"Data created for {evento_reporte.nombre}")
    print(f"Alice: 100%, Bob: 50%, Charlie: 0%")

if __name__ == '__main__':
    create_demo_data()
