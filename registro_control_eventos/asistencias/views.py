"""
Vistas para la aplicación de Asistencias
Placeholder - Implementar según necesidades
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def lista_asistencias(request):
    """Lista eventos para gestión de asistencias"""
    from eventos.models import Evento
    from django.db.models import Count, Q
    
    if not request.user.puede_gestionar_eventos():
        messages.error(request, 'No tiene permisos')
        return redirect('dashboard:index')
    
    # List events that have registrations
    eventos = Evento.objects.filter(
        estado__in=['PUBLICADO', 'EN_CURSO', 'FINALIZADO']
    ).annotate(
        inscritos_count=Count('inscripciones', filter=Q(inscripciones__estado='CONFIRMADA'))
    ).filter(inscritos_count__gt=0).order_by('-fecha_inicio')
    
    context = {
        'eventos': eventos
    }
    
    return render(request, 'asistencias/lista.html', context)


@login_required
def control_asistencias(request):
    return render(request, 'asistencias/control.html')


@login_required
def registrar_asistencia(request, inscripcion_id):
    """Registra asistencia para una inscripción"""
    from inscripciones.models import Inscripcion
    from asistencias.models import Asistencia
    from django.shortcuts import get_object_or_404
    
    if not request.user.puede_gestionar_eventos():
        messages.error(request, 'No tiene permisos')
        return redirect('dashboard:index')
    
    inscripcion = get_object_or_404(Inscripcion, pk=inscripcion_id)
    
    if request.method == 'POST':
        sesion = request.POST.get('sesion', 1)
        try:
            sesion = int(sesion)
        except ValueError:
            sesion = 1
        
        # Check if attendance already exists for this session
        if Asistencia.objects.filter(inscripcion=inscripcion, sesion=sesion).exists():
            messages.warning(request, f'La asistencia para la sesión {sesion} ya fue registrada.')
        else:
            try:
                Asistencia.registrar_manual(
                    inscripcion=inscripcion,
                    sesion=sesion,
                    usuario=request.user
                )
                messages.success(request, f'Asistencia registrada para {inscripcion.get_nombre_completo()} - Sesión {sesion}')
            except ValueError as e:
                messages.error(request, str(e))
    
    return redirect('asistencias:evento', evento_id=inscripcion.evento.pk)


def registrar_qr(request, codigo_qr):
    return render(request, 'asistencias/qr.html')


@login_required
def asistencias_evento(request, evento_id):
    """Gestión de asistencias para un evento específico"""
    from eventos.models import Evento
    from inscripciones.models import Inscripcion
    from django.shortcuts import get_object_or_404
    
    if not request.user.puede_gestionar_eventos():
        messages.error(request, 'No tiene permisos')
        return redirect('dashboard:index')
    
    evento = get_object_or_404(Evento, pk=evento_id)
    inscripciones = Inscripcion.objects.filter(
        evento=evento,
        estado='CONFIRMADA'
    ).select_related('usuario').prefetch_related('asistencias').order_by('apellido', 'nombre')
    
    # Add session tracking for each inscripcion
    participantes = []
    for inscripcion in inscripciones:
        sesiones_registradas = list(inscripcion.asistencias.values_list('sesion', flat=True))
        sesiones_disponibles = [s for s in range(1, evento.numero_sesiones + 1) if s not in sesiones_registradas]
        
        # Check for certificate
        from certificados.models import Certificado
        certificado = Certificado.objects.filter(inscripcion=inscripcion).first()
        
        participantes.append({
            'inscripcion': inscripcion,
            'sesiones_registradas': sesiones_registradas,
            'sesiones_disponibles': sesiones_disponibles,
            'todas_registradas': len(sesiones_disponibles) == 0,
            'certificado': certificado,
            'puede_generar_certificado': inscripcion.puede_generar_certificado
        })
    
    context = {
        'evento': evento,
        'participantes': participantes
    }
    
    return render(request, 'asistencias/evento.html', context)


