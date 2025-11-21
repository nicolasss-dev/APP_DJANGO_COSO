import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'registro_control_eventos.settings')
django.setup()

from eventos.models import Evento
from certificados.models import Certificado

# Get the demo event
evento = Evento.objects.filter(nombre='Taller de Certificación Automática').first()

if evento:
    print(f"Found event: {evento.nombre} (ID: {evento.id})")
    print(f"Generates certificates: {evento.genera_certificado}")
    print(f"Status: {evento.estado}")
    
    # Try to generate certificates
    print("\nAttempting to generate certificates...")
    try:
        certificados = Certificado.generar_certificados_evento(evento)
        print(f"SUCCESS: Generated {len(certificados)} certificates")
        
        for cert in certificados:
            print(f"  - {cert.inscripcion.get_nombre_completo()}: {cert.codigo_verificacion}")
            print(f"    PDF: {'Yes' if cert.archivo_pdf else 'No'}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
else:
    print("Event not found!")
