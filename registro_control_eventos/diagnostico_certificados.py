import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'registro_control_eventos.settings')
django.setup()

from certificados.models import Certificado
from inscripciones.models import Inscripcion
from usuarios.models import Usuario

print("=" * 60)
print("DIAGNÓSTICO DE CERTIFICADOS")
print("=" * 60)

# Listar todos los certificados
certificados = Certificado.objects.all().select_related('inscripcion__usuario', 'inscripcion__evento')
print(f"\n📋 Total de certificados en la base de datos: {certificados.count()}")

for cert in certificados:
    print(f"\n--- Certificado #{cert.pk} ---")
    print(f"  Código: {cert.codigo_verificacion}")
    print(f"  Inscripción ID: {cert.inscripcion.pk}")
    print(f"  Usuario: {cert.inscripcion.usuario if cert.inscripcion.usuario else 'Sin usuario'}")
    print(f"  Email: {cert.inscripcion.correo}")
    print(f"  Evento: {cert.inscripcion.evento.nombre}")
    print(f"  Tiene PDF: {'✓ Sí' if cert.archivo_pdf else '✗ No'}")
    print(f"  Estado: {cert.estado}")
    print(f"  Fecha generación: {cert.fecha_generacion}")

# Listar inscripciones elegibles sin certificado
print("\n" + "=" * 60)
print("INSCRIPCIONES ELEGIBLES SIN CERTIFICADO")
print("=" * 60)

inscripciones = Inscripcion.objects.filter(estado='CONFIRMADA').select_related('evento', 'usuario')
elegibles_sin_cert = []

for insc in inscripciones:
    tiene_cert = hasattr(insc, 'certificado') and insc.certificado is not None
    if insc.puede_generar_certificado and not tiene_cert:
        elegibles_sin_cert.append(insc)
        print(f"\n--- Inscripción #{insc.pk} ---")
        print(f"  Usuario: {insc.usuario if insc.usuario else 'Sin usuario'}")
        print(f"  Email: {insc.correo}")
        print(f"  Evento: {insc.evento.nombre}")
        print(f"  % Asistencia: {insc.porcentaje_asistencia}%")
        print(f"  Puede generar: {'✓ Sí' if insc.puede_generar_certificado else '✗ No'}")

print(f"\n\n💡 Total elegibles sin certificado: {len(elegibles_sin_cert)}")

# Verificar usuarios
print("\n" + "=" * 60)
print("USUARIOS EN EL SISTEMA")
print("=" * 60)

usuarios = Usuario.objects.all()
print(f"Total usuarios: {usuarios.count()}")

for user in usuarios:
    print(f"\n--- Usuario: {user.username} ---")
    print(f"  Email: {user.email}")
    print(f"  Rol: {user.rol}")
    print(f"  Es staff: {user.is_staff}")
    
    # Inscripciones del usuario
    inscripciones_usuario = Inscripcion.objects.filter(usuario=user)
    print(f"  Inscripciones (por usuario): {inscripciones_usuario.count()}")
    
    # Por email
    inscripciones_email = Inscripcion.objects.filter(correo=user.email)
    print(f"  Inscripciones (por email): {inscripciones_email.count()}")
    
    # Certificados
    certificados_usuario = Certificado.objects.filter(inscripcion__usuario=user)
    print(f"  Certificados (por usuario): {certificados_usuario.count()}")
    
    certificados_email = Certificado.objects.filter(inscripcion__correo=user.email)
    print(f"  Certificados (por email): {certificados_email.count()}")

print("\n" + "=" * 60)
