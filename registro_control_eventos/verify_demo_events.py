import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'registro_control_eventos.settings')
django.setup()

from eventos.models import Evento
from inscripciones.models import Inscripcion
from asistencias.models import Asistencia
from certificados.models import Certificado

def verify_demo_events():
    print("Verifying demo events...\n")
    
    # Check for automatic certificate event
    cert_event = Evento.objects.filter(nombre='Taller de Certificación Automática').first()
    if cert_event:
        print(f"✓ Found: {cert_event.nombre} (ID: {cert_event.id})")
        inscriptions = Inscripcion.objects.filter(evento=cert_event, estado='CONFIRMADA')
        print(f"  - Inscriptions: {inscriptions.count()}")
        for insc in inscriptions:
            attendance = Asistencia.objects.filter(inscripcion=insc).count()
            print(f"    * {insc.get_nombre_completo()}: {attendance}/{cert_event.numero_sesiones} sessions")
            cert = Certificado.objects.filter(inscripcion=insc).first()
            if cert:
                print(f"      Certificate: {cert.codigo_verificacion} ({'Generated' if cert.archivo_pdf else 'Not generated'})")
    else:
        print("✗ 'Taller de Certificación Automática' NOT FOUND")
    
    print()
    
    # Check for attendance report event
    report_event = Evento.objects.filter(nombre='Seminario de Análisis de Datos').first()
    if report_event:
        print(f"✓ Found: {report_event.nombre} (ID: {report_event.id})")
        inscriptions = Inscripcion.objects.filter(evento=report_event, estado='CONFIRMADA')
        print(f"  - Inscriptions: {inscriptions.count()}")
        for insc in inscriptions:
            attendance = Asistencia.objects.filter(inscripcion=insc).count()
            percentage = (attendance / report_event.numero_sesiones * 100) if report_event.numero_sesiones > 0 else 0
            print(f"    * {insc.get_nombre_completo()}: {attendance}/{report_event.numero_sesiones} sessions ({percentage:.0f}%)")
    else:
        print("✗ 'Seminario de Análisis de Datos' NOT FOUND")
    
    print("\n" + "="*50)
    print("All events in database:")
    all_events = Evento.objects.all()
    if all_events.exists():
        for evt in all_events:
            print(f"  - {evt.nombre} (ID: {evt.id}, Estado: {evt.estado})")
    else:
        print("  No events found in database!")

if __name__ == '__main__':
    verify_demo_events()
