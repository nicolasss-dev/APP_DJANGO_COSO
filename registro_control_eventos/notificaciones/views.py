"""
Vistas para la aplicación de Notificaciones
PRCE - Plataforma de Registro y Control de Eventos

HU-21: Confirmación de Inscripción
HU-22: Recordatorios Previos
HU-23: Notificación de Cambios o Cancelación
HU-24: Plantillas de Correo Personalizables
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from django.http import JsonResponse
import time

from .models import Notificacion, PlantillaCorreo, TipoNotificacion, ConfiguracionRecordatorio
from .forms import (
    EnviarNotificacionForm,
    PlantillaCorreoForm,
    NotificacionRapidaForm,
    ConfiguracionRecordatorioForm
)
from eventos.models import Evento
from inscripciones.models import Inscripcion
from usuarios.models import Usuario


@login_required
def lista_notificaciones(request):
    """Lista de notificaciones enviadas"""
    if not request.user.puede_gestionar_eventos():
        messages.error(request, 'No tiene permisos')
        return redirect('dashboard:index')
    
    # Filtros
    estado = request.GET.get('estado', '')
    tipo = request.GET.get('tipo', '')
    
    notificaciones = Notificacion.objects.select_related('tipo_notificacion', 'evento').all()
    
    if estado:
        notificaciones = notificaciones.filter(estado=estado)
    if tipo:
        notificaciones = notificaciones.filter(tipo_notificacion__codigo=tipo)
    
    # Estadísticas
    total = notificaciones.count()
    enviadas = notificaciones.filter(estado='ENVIADO').count()
    pendientes = notificaciones.filter(estado='PENDIENTE').count()
    errores = notificaciones.filter(estado='ERROR').count()
    
    context = {
        'notificaciones': notificaciones.order_by('-fecha_programada')[:100],
        'tipos': TipoNotificacion.objects.all(),
        'total': total,
        'enviadas': enviadas,
        'pendientes': pendientes,
        'errores': errores,
        'estado_filter': estado,
        'tipo_filter': tipo,
    }
    
    return render(request, 'notificaciones/lista.html', context)


@login_required
def enviar_notificacion_manual(request):
    """Enviar notificación manual (SIMULADO)"""
    if not request.user.puede_gestionar_eventos():
        messages.error(request, 'No tiene permisos')
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = NotificacionRapidaForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['destinatario_email']
            asunto = form.cleaned_data['asunto']
            mensaje = form.cleaned_data['mensaje']
            
            # Crear notificación (SIMULADA)
            notificacion = Notificacion.objects.create(
                tipo_notificacion=TipoNotificacion.objects.first(),
                destinatario_email=email,
                asunto=asunto,
                cuerpo=mensaje,
                estado='ENVIADO',  # SIMULADO: marcar como enviado
                fecha_envio=timezone.now()
            )
            
            messages.success(request, f'✓ Notificación enviada a {email}')
            return redirect('notificaciones:detalle', notificacion_id=notificacion.id)
    else:
        form = NotificacionRapidaForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'notificaciones/enviar_manual.html', context)


@login_required
def detalle_notificacion(request, notificacion_id):
    """Ver detalles de una notificación"""
    notificacion = get_object_or_404(Notificacion, pk=notificacion_id)
    
    context = {
        'notificacion': notificacion,
    }
    
    return render(request, 'notificaciones/detalle.html', context)


@login_required
def lista_plantillas(request):
    """Lista de plantillas de correo"""
    if not request.user.puede_gestionar_eventos():
        messages.error(request, 'No tiene permisos')
        return redirect('dashboard:index')
    
    plantillas = PlantillaCorreo.objects.select_related('tipo_notificacion').all()
    
    context = {
        'plantillas': plantillas,
    }
    
    return render(request, 'notificaciones/plantillas_lista.html', context)


@login_required
def crear_plantilla(request):
    """Crear nueva plantilla de correo"""
    if not request.user.puede_gestionar_eventos():
        messages.error(request, 'No tiene permisos')
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = PlantillaCorreoForm(request.POST)
        if form.is_valid():
            plantilla = form.save(commit=False)
            plantilla.creada_por = request.user
            plantilla.save()
            messages.success(request, '✓ Plantilla creada exitosamente')
            return redirect('notificaciones:plantillas')
    else:
        form = PlantillaCorreoForm()
    
    context = {
        'form': form,
        'modo': 'crear',
    }
    
    return render(request, 'notificaciones/plantilla_form.html', context)


@login_required
def editar_plantilla(request, plantilla_id):
    """Editar plantilla de correo"""
    if not request.user.puede_gestionar_eventos():
        messages.error(request, 'No tiene permisos')
        return redirect('dashboard:index')
    
    plantilla = get_object_or_404(PlantillaCorreo, pk=plantilla_id)
    
    if request.method == 'POST':
        form = PlantillaCorreoForm(request.POST, instance=plantilla)
        if form.is_valid():
            form.save()
            messages.success(request, '✓ Plantilla actualizada')
            return redirect('notificaciones:plantillas')
    else:
        form = PlantillaCorreoForm(instance=plantilla)
    
    context = {
        'form': form,
        'plantilla': plantilla,
        'modo': 'editar',
    }
    
    return render(request, 'notificaciones/plantilla_form.html', context)


@login_required
def preview_plantilla(request, plantilla_id):
    """Vista previa de plantilla renderizada"""
    plantilla = get_object_or_404(PlantillaCorreo, pk=plantilla_id)
    
    # Contexto de ejemplo
    contexto_ejemplo = {
        'nombre': 'Juan Pérez',
        'evento': {
            'nombre': 'Conferencia de Tecnología 2025',
            'fecha_inicio': timezone.now(),
            'lugar': 'Centro de Convenciones',
        },
        'inscripcion': {
            'codigo_qr': 'ABC123XYZ',
        },
        'fecha': timezone.now(),
    }
    
    # Renderizar plantilla
    contenido = plantilla.renderizar(contexto_ejemplo)
    
    context = {
        'plantilla': plantilla,
        'asunto': contenido['asunto'],
        'cuerpo_texto': contenido['cuerpo_texto'],
        'cuerpo_html': contenido['cuerpo_html'],
        'contexto': contexto_ejemplo,
    }
    
    return render(request, 'notificaciones/preview.html', context)
