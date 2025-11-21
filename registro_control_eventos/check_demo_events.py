import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'registro_control_eventos.settings')
django.setup()

from eventos.models import Evento
from inscripciones.models import Inscripcion
from asistencias.models import Asistencia
from certificados.models import Certificado

print("\n" + "="*70)
print("DEMO EVENTS VERIFICATION")
print("="*70 + "\n")

# Look for demo events
demo_event_names = [
    'Taller de Certificación Automática',
    'Seminario de Análisis de Datos'
]

found_events = []
for name in demo_event_names:
    evt = Evento.objects.filter(nombre=name).first()
    if evt:
        found_events.append(evt)
        print(f"✓ FOUND: {evt.nombre}")
        print(f"  ID: {evt.id}")
        print(f"  Estado: {evt.estado}")
        print(f"  Sesiones: {evt.numero_sesiones}")
        
        # Check inscriptions
        inscritos = Inscripcion.objects.filter(evento=evt, estado='CONFIRMADA')
        print(f"  Inscripciones confirmadas: {inscritos.count()}")
        
        for insc in inscritos:
            asist_count = Asistencia.objects.filter(inscripcion=insc).count()
            pct = (asist_count / evt.numero_sesiones * 100) if evt.numero_sesiones > 0 else 0
            print(f"    - {insc.get_nombre_completo()}: {asist_count}/{evt.numero_sesiones} ({pct:.0f}%)")
            
            cert = Certificado.objects.filter(inscripcion=insc).first()
            if cert:
                print(f"      -> Certificado: {cert.codigo_verificacion}")
        
        print()
    else:
        print(f"✗ NOT FOUND: {name}\n")

print("="*70)
print(f"Total demo events found: {len(found_events)}/2")
print("="*70)

if len(found_events) < 2:
    print("\n⚠ MISSING EVENTS - Running create_demo_data.py now...\n")
    exec(open('create_demo_data.py').read())
    print("\n✓ Demo data creation completed!")
else:
    print("\n✓ All demo events exist!")
    print("\nYou can access them at:")
    for evt in found_events:
        print(f"  - Attendance Report: http://localhost:8000/reportes/asistencia/{evt.id}/")
