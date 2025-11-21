"""
Vistas para la aplicación de Certificados
Placeholder - Implementar según necesidades
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Certificado
from inscripciones.models import Inscripcion


@login_required
def lista_certificados(request):
    """Lista de certificados del usuario"""
    from django.db.models import Q
    certificados = Certificado.objects.filter(
        Q(inscripcion__usuario=request.user) | 
        Q(inscripcion__correo=request.user.email)
    ).select_related('inscripcion__evento')
    return render(request, 'certificados/lista.html', {'certificados': certificados})


@login_required
def generar_masivo(request, evento_id=None):
    """Lista eventos y genera certificados masivos"""
    from eventos.models import Evento
    from django.db.models import Count, Q
    
    if not request.user.puede_gestionar_eventos():
        messages.error(request, 'No tiene permisos')
        return redirect('dashboard:index')
    
    # If evento_id is provided, generate certificates for that event
    if evento_id:
        evento = get_object_or_404(Evento, pk=evento_id)
        
        try:
            certificados_generados = Certificado.generar_certificados_evento(evento)
            
            if len(certificados_generados) > 0:
                messages.success(
                    request, 
                    f'✓ Se generaron {len(certificados_generados)} certificado(s) para {evento.nombre}. '
                    f'Los certificados están disponibles en la lista de certificados de cada participante.'
                )
            else:
                messages.warning(
                    request,
                    f'No se generaron certificados para {evento.nombre}. '
                    f'Verifica que los participantes cumplan con el porcentaje mínimo de asistencia ({evento.porcentaje_asistencia_minimo}%).'
                )
        except Exception as e:
            messages.error(request, f'Error al generar certificados: {str(e)}')
            import logging
            logging.error(f'Certificate generation error: {e}', exc_info=True)
        
        return redirect('certificados:generar_masivo')
    
    # List events that can generate certificates (show all events with this feature enabled)
    eventos = Evento.objects.filter(
        genera_certificado=True
    ).annotate(
        inscritos_count=Count('inscripciones', filter=Q(inscripciones__estado='CONFIRMADA'))
    ).filter(inscritos_count__gt=0).order_by('-fecha_fin')
    
    context = {
        'eventos': eventos
    }
    
    return render(request, 'certificados/generar_masivo.html', context)


@login_required
def generar_certificado(request, inscripcion_id):
    """Genera un certificado individualmente"""
    inscripcion = get_object_or_404(Inscripcion, pk=inscripcion_id)
    
    # Verificar permisos (solo admin o el propio usuario si cumple requisitos)
    es_propietario = (inscripcion.usuario == request.user) or (inscripcion.correo == request.user.email)
    if not (request.user.is_staff or es_propietario):
        messages.error(request, 'No tiene permisos para generar este certificado')
        return redirect('dashboard:index')
        
    if not inscripcion.puede_generar_certificado:
        messages.error(request, 'No cumple los requisitos para generar el certificado')
        return redirect('dashboard:index')

    certificado, created = Certificado.objects.get_or_create(inscripcion=inscripcion)
    if not certificado.archivo_pdf:
        certificado.generar_pdf()
        
    messages.success(request, 'Certificado generado exitosamente')
    # Redirect to download the certificate
    return redirect('certificados:descargar', certificado_id=certificado.pk)


@login_required
def descargar_certificado(request, certificado_id):
    """Descarga el archivo PDF del certificado"""
    certificado = get_object_or_404(Certificado, pk=certificado_id)
    
    # Verificar permisos
    es_propietario = (certificado.inscripcion.usuario == request.user) or (certificado.inscripcion.correo == request.user.email)
    if not (request.user.is_staff or es_propietario):
        messages.error(request, 'No tiene permisos para descargar este certificado')
        return redirect('dashboard:index')
        
    if not certificado.archivo_pdf:
        certificado.generar_pdf()
        
    # Simulación: En lugar de descargar archivo, mostrar vista previa HTML
    return render(request, 'certificados/ver_certificado.html', {'certificado': certificado})
    
    # Código original comentado para referencia
    # response = HttpResponse(certificado.archivo_pdf, content_type='application/pdf')
    # response['Content-Disposition'] = f'attachment; filename="certificado_{certificado.codigo_verificacion}.pdf"'
    # return response


@login_required
def enviar_certificado(request, certificado_id):
    """Envía el certificado por correo"""
    if not request.user.is_staff:
        messages.error(request, 'No tiene permisos')
        return redirect('dashboard:index')
        
    certificado = get_object_or_404(Certificado, pk=certificado_id)
    if certificado.enviar_por_correo():
        messages.success(request, 'Certificado enviado por correo')
    else:
        messages.error(request, 'Error al enviar el certificado')
        
    return redirect('certificados:lista')


def verificar_certificado(request, codigo):
    """Verifica la validez de un certificado"""
    certificado = get_object_or_404(Certificado, codigo_verificacion=codigo)
    return render(request, 'certificados/verificar.html', {'certificado': certificado})
