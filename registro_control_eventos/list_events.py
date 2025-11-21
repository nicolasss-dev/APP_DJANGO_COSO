import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'registro_control_eventos.settings')
django.setup()

from eventos.models import Evento

print("\n=== ALL EVENTS IN DATABASE ===\n")
eventos = Evento.objects.all().order_by('-fecha_creacion')

if not eventos.exists():
    print("No events found!")
else:
    for evt in eventos:
        print(f"ID: {evt.id}")
        print(f"Name: {evt.nombre}")
        print(f"Status: {evt.estado}")
        print(f"URL: http://localhost:8000/eventos/{evt.id}/")
        
        # Check inscriptions
        from inscripciones.models import Inscripcion
        inscritos = Inscripcion.objects.filter(evento=evt, estado='CONFIRMADA').count()
        print(f"Confirmed registrations: {inscritos}")
        
        if evt.nombre in ['Taller de Certificación Automática', 'Seminario de Análisis de Datos']:
            print(f"*** DEMO EVENT - Report URL: http://localhost:8000/reportes/asistencia/{evt.id}/")
        
        print("-" * 60)
