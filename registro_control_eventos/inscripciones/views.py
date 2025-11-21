"""
Vistas para la aplicación de Inscripciones
Placeholder - Implementar según necesidades
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction, models
from django.utils import timezone

from eventos.models import Evento
from inscripciones.models import Inscripcion
from .forms import InscripcionPublicaForm


@login_required
def lista_inscripciones(request):
    """
    Lista de inscripciones con filtros y búsqueda
    Administradores/Organizadores: ven todas las inscripciones
    Asistentes: ven solo sus propias inscripciones
    """
    from django.db.models import Q
    
    user = request.user
    
    # Base query según permisos
    if user.puede_gestionar_eventos():
        # Administradores y Organizadores ven todas las inscripciones
        if user.es_organizador() and not user.es_administrador():
            # Organizadores solo ven inscripciones de sus eventos
            inscripciones = Inscripcion.objects.filter(
                evento__creado_por=user
            ).select_related('evento', 'usuario').order_by('-fecha_inscripcion')
        else:
            # Administradores ven todas
            inscripciones = Inscripcion.objects.all().select_related('evento', 'usuario').order_by('-fecha_inscripcion')
    else:
        # Asistentes ven solo sus propias inscripciones
        inscripciones = Inscripcion.objects.filter(
            Q(usuario=user) | Q(correo=user.email)
        ).select_related('evento', 'usuario').order_by('-fecha_inscripcion')
    
    # Filtros
    evento_filtro = request.GET.get('evento')
    estado_filtro = request.GET.get('estado')
    busqueda = request.GET.get('q', '').strip()
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    # Aplicar filtros
    if evento_filtro:
        try:
            inscripciones = inscripciones.filter(evento_id=int(evento_filtro))
        except (ValueError, TypeError):
            pass
    
    if estado_filtro:
        inscripciones = inscripciones.filter(estado=estado_filtro)
    
    if busqueda:
        inscripciones = inscripciones.filter(
            Q(nombre__icontains=busqueda) |
            Q(apellido__icontains=busqueda) |
            Q(correo__icontains=busqueda) |
            Q(documento__icontains=busqueda) |
            Q(evento__nombre__icontains=busqueda)
        )
    
    if fecha_desde:
        try:
            from datetime import datetime
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d')
            inscripciones = inscripciones.filter(fecha_inscripcion__gte=fecha_desde_obj)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            from datetime import datetime
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            inscripciones = inscripciones.filter(fecha_inscripcion__lte=fecha_hasta_obj)
        except ValueError:
            pass
    
    # Obtener eventos para filtro (solo para administradores/organizadores)
    eventos_para_filtro = None
    if user.puede_gestionar_eventos():
        if user.es_organizador() and not user.es_administrador():
            eventos_para_filtro = Evento.objects.filter(creado_por=user).order_by('nombre')
        else:
            eventos_para_filtro = Evento.objects.all().order_by('nombre')
    
    context = {
        'inscripciones': inscripciones,
        'eventos_para_filtro': eventos_para_filtro,
        'filtros_activos': {
            'evento': evento_filtro,
            'estado': estado_filtro,
            'q': busqueda,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
        },
        'total_inscripciones': inscripciones.count(),
    }
    
    return render(request, 'inscripciones/lista.html', context)


def registro_publico(request):
    """
    Vista pública para mostrar eventos disponibles y permitir registro (HU-03)
    Accesible sin login - muestra solo eventos PUBLICADOS con cupos disponibles
    """
    # Obtener eventos publicados con cupos disponibles y fecha futura
    eventos = Evento.objects.filter(
        estado='PUBLICADO',
        fecha_inicio__gt=timezone.now()
    ).select_related('tipo_evento').order_by('fecha_inicio')
    
    # Filtrar eventos con cupos disponibles
    eventos_disponibles = [evento for evento in eventos if not evento.esta_lleno]
    
    context = {
        'eventos': eventos_disponibles,
        'total_eventos': len(eventos_disponibles)
    }
    
    return render(request, 'inscripciones/registro_publico.html', context)


def registro_publico_evento(request, evento_id):
    """
    Formulario público de inscripción a un evento específico (HU-03)
    Implementación completa del proceso de registro
    """
    evento = get_object_or_404(Evento, pk=evento_id)
    
    # Verificar que el evento pueda recibir inscripciones
    if not evento.puede_inscribirse:
        messages.error(request, 'Este evento no está disponible para inscripciones')
        return redirect('eventos:detalle', pk=evento_id)
    
    # Verificar cupos disponibles (HU-03, Criterio 5)
    if evento.esta_lleno:
        messages.error(request, 'Evento sin cupos disponibles')
        return redirect('eventos:detalle', pk=evento_id)
    
    # Verificar si el usuario ya está inscrito
    inscripcion_existente = None
    if request.user.is_authenticated:
        inscripcion_existente = Inscripcion.objects.filter(
            evento=evento,
            usuario=request.user
        ).first()

    if request.method == 'POST':
        if inscripcion_existente:
             if inscripcion_existente.estado == 'PENDIENTE' and not evento.es_gratuito:
                 messages.info(request, 'Ya tienes una inscripción pendiente. Por favor completa el pago.')
                 return redirect('pagos:seleccionar_metodo', inscripcion_id=inscripcion_existente.pk)
             
             messages.warning(request, f'Ya te encuentras registrado en este evento con estado: {inscripcion_existente.get_estado_display()}')
             return redirect('inscripciones:detalle', pk=inscripcion_existente.pk)

        form = InscripcionPublicaForm(request.POST, evento=evento, usuario=request.user if request.user.is_authenticated else None)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Verificar cupos nuevamente (por si cambió mientras llenaba el formulario)
                    if evento.esta_lleno:
                        messages.error(request, 'Lo sentimos, el evento se ha llenado mientras completaba el formulario.')
                        form = InscripcionPublicaForm(evento=evento, usuario=request.user if request.user.is_authenticated else None)
                        return render(request, 'inscripciones/registro_publico_evento.html', {
                            'evento': evento,
                            'form': form
                        })
                    
                    # Crear inscripción
                    inscripcion = form.save(commit=False)
                    inscripcion.evento = evento
                    
                    # Si el usuario está autenticado, asociar usuario
                    if request.user.is_authenticated:
                        inscripcion.usuario = request.user
                    
                    # Validar documento único antes de guardar
                    if Inscripcion.objects.filter(evento=evento, documento=inscripcion.documento).exists():
                        messages.error(request, 'Ya existe una inscripción con este documento para este evento.')
                        form = InscripcionPublicaForm(evento=evento, usuario=request.user if request.user.is_authenticated else None)
                        return render(request, 'inscripciones/registro_publico_evento.html', {
                            'evento': evento,
                            'form': form
                        })
                    
                    # El modelo se encarga de auto-confirmar si es gratuito
                    inscripcion.save()
                    
                    # Mensaje de éxito según tipo de evento
                    if evento.es_gratuito:
                        messages.success(
                            request,
                            f'¡Inscripción confirmada exitosamente! '
                            f'Se ha enviado un correo de confirmación a {inscripcion.correo}'
                        )
                        # Redirigir a página de confirmación
                        return redirect('inscripciones:confirmacion_inscripcion', pk=inscripcion.pk)
                    else:
                        messages.info(
                            request,
                            f'¡Inscripción iniciada! Para confirmar su cupo, por favor realice el pago.'
                        )
                        # Redirigir a selección de método de pago
                        return redirect('pagos:seleccionar_metodo', inscripcion_id=inscripcion.pk)
                    
            except Exception as e:
                # Log detallado del error
                import logging
                import traceback
                logger = logging.getLogger(__name__)
                error_detail = traceback.format_exc()
                logger.error(f'Error en inscripción - Evento: {evento.pk}, Usuario: {request.user if request.user.is_authenticated else "Anónimo"}\n{error_detail}')
                
                # Mensaje de error más específico
                error_msg = str(e)
                if 'documento' in error_msg.lower() or 'unique' in error_msg.lower():
                    # Intentar buscar la inscripción existente para redirigir
                    documento = form.cleaned_data.get('documento')
                    email = form.cleaned_data.get('correo')
                    
                    inscripcion_dup = Inscripcion.objects.filter(
                        evento=evento,
                        documento=documento
                    ).first()
                    
                    if inscripcion_dup:
                        if inscripcion_dup.estado == 'PENDIENTE' and not evento.es_gratuito:
                            messages.info(request, 'Ya existe una inscripción con este documento. Por favor completa el pago.')
                            return redirect('pagos:seleccionar_metodo', inscripcion_id=inscripcion_dup.pk)
                        elif request.user.is_authenticated and inscripcion_dup.usuario == request.user:
                             return redirect('inscripciones:detalle', pk=inscripcion_dup.pk)
                    
                    messages.error(request, 'Ya existe una inscripción con este documento o correo para este evento.')
                elif 'cupo' in error_msg.lower() or 'lleno' in error_msg.lower():
                    messages.error(request, 'El evento ya no tiene cupos disponibles.')
                else:
                    messages.error(
                        request,
                        f'Ocurrió un error al procesar su inscripción: {error_msg}. '
                        f'Por favor intente nuevamente o contacte al administrador.'
                    )
        else:
            # Mostrar errores del formulario de forma más clara
            for field, errors in form.errors.items():
                for error in errors:
                    # Check if error is about duplicate registration
                    if 'Ya se encuentra inscrito' in error or 'Ya existe una inscripción' in error:
                        documento = form.data.get('documento')
                        email = form.data.get('correo')
                        
                        inscripcion_dup = Inscripcion.objects.filter(
                            evento=evento
                        ).filter(
                            models.Q(documento=documento) | models.Q(correo=email)
                        ).first()
                        
                        if inscripcion_dup:
                            if inscripcion_dup.estado == 'PENDIENTE' and not evento.es_gratuito:
                                messages.info(request, 'Ya existe una inscripción con este documento/correo. Por favor completa el pago.')
                                return redirect('pagos:seleccionar_metodo', inscripcion_id=inscripcion_dup.pk)
                            elif request.user.is_authenticated and inscripcion_dup.usuario == request.user:
                                 return redirect('inscripciones:detalle', pk=inscripcion_dup.pk)

                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        field_name = form.fields[field].label if field in form.fields else field
                        messages.error(request, f'{field_name}: {error}')
    else:
        form = InscripcionPublicaForm(evento=evento, usuario=request.user if request.user.is_authenticated else None)
    
    context = {
        'evento': evento,
        'form': form,
        'inscripcion_existente': inscripcion_existente
    }
    return render(request, 'inscripciones/registro_publico_evento.html', context)


def confirmacion_inscripcion(request, pk):
    """
    Página de confirmación después de inscripción exitosa (HU-03)
    """
    inscripcion = get_object_or_404(Inscripcion, pk=pk)
    
    context = {
        'inscripcion': inscripcion,
        'evento': inscripcion.evento
    }
    return render(request, 'inscripciones/confirmacion.html', context)


@login_required
def registro_masivo(request):
    return render(request, 'inscripciones/registro_masivo.html')


@login_required
def detalle_inscripcion(request, pk):
    """
    Detalle de una inscripción
    """
    inscripcion = get_object_or_404(Inscripcion, pk=pk)
    
    # Verificar permisos
    user = request.user
    if not user.puede_gestionar_eventos():
        # Asistentes solo pueden ver sus propias inscripciones
        if inscripcion.usuario != user and inscripcion.correo != user.email:
            messages.error(request, 'No tiene permisos para ver esta inscripción')
            return redirect('inscripciones:lista')
    
    # Obtener certificado si existe
    from certificados.models import Certificado
    certificado = Certificado.objects.filter(inscripcion=inscripcion).first()

    context = {
        'inscripcion': inscripcion,
        'evento': inscripcion.evento,
        'puede_editar': user.puede_gestionar_eventos(),
        'certificado': certificado,
    }
    
    return render(request, 'inscripciones/detalle.html', context)


@login_required
def confirmar_inscripcion(request, pk):
    """
    Confirmar una inscripción (solo Administradores/Organizadores)
    """
    if not request.user.puede_gestionar_eventos():
        messages.error(request, 'No tiene permisos para confirmar inscripciones')
        return redirect('inscripciones:lista')
    
    inscripcion = get_object_or_404(Inscripcion, pk=pk)
    
    if inscripcion.estado == 'CONFIRMADA':
        messages.warning(request, 'La inscripción ya está confirmada')
        return redirect('inscripciones:detalle', pk=pk)
    
    try:
        with transaction.atomic():
            inscripcion.confirmar()
            messages.success(request, f'Inscripción de {inscripcion.get_nombre_completo()} confirmada exitosamente')
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error al confirmar inscripción: {str(e)}')
        messages.error(request, f'Error al confirmar inscripción: {str(e)}')
    
    return redirect('inscripciones:detalle', pk=pk)


@login_required
def cancelar_inscripcion(request, pk):
    """
    Cancelar una inscripción
    """
    inscripcion = get_object_or_404(Inscripcion, pk=pk)
    
    # Verificar permisos
    user = request.user
    if not user.puede_gestionar_eventos():
        # Asistentes solo pueden cancelar sus propias inscripciones
        if inscripcion.usuario != user and inscripcion.correo != user.email:
            messages.error(request, 'No tiene permisos para cancelar esta inscripción')
            return redirect('inscripciones:lista')
    
    if inscripcion.estado == 'CANCELADA':
        messages.warning(request, 'La inscripción ya está cancelada')
        return redirect('inscripciones:detalle', pk=pk)
    
    try:
        with transaction.atomic():
            inscripcion.cancelar()
            messages.success(request, f'Inscripción de {inscripcion.get_nombre_completo()} cancelada exitosamente')
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error al cancelar inscripción: {str(e)}')
        messages.error(request, f'Error al cancelar inscripción: {str(e)}')
    
    return redirect('inscripciones:detalle', pk=pk)
