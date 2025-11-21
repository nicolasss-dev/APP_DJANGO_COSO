"""
Vistas para la aplicación de Eventos
HU-01: Creación de Eventos
HU-02: Edición de Eventos
HU-06: Eliminación de Eventos
HU-09: Duplicar Evento Existente
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Evento
from .forms import EventoForm


@login_required
def lista_eventos(request):
    """Lista de eventos con filtros y búsqueda"""
    from django.db.models import Q
    from django.utils import timezone
    
    # Base query según permisos
    if request.user.puede_gestionar_eventos():
        eventos = Evento.objects.select_related('tipo_evento', 'creado_por').all()
    else:
        eventos = Evento.objects.filter(estado='PUBLICADO').select_related('tipo_evento')
    
    # Filtros
    tipo_filtro = request.GET.get('tipo')
    estado_filtro = request.GET.get('estado')
    busqueda = request.GET.get('q', '').strip()
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    # Aplicar filtros
    if tipo_filtro:
        eventos = eventos.filter(tipo_evento__nombre=tipo_filtro)
    
    if estado_filtro:
        eventos = eventos.filter(estado=estado_filtro)
    
    if busqueda:
        eventos = eventos.filter(
            Q(nombre__icontains=busqueda) |
            Q(descripcion__icontains=busqueda) |
            Q(lugar__icontains=busqueda)
        )
    
    if fecha_desde:
        try:
            from datetime import datetime
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d')
            eventos = eventos.filter(fecha_inicio__gte=fecha_desde_obj)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            from datetime import datetime
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            eventos = eventos.filter(fecha_inicio__lte=fecha_hasta_obj)
        except ValueError:
            pass
    
    # Ordenar
    orden = request.GET.get('orden', '-fecha_inicio')
    eventos = eventos.order_by(orden)
    
    # Obtener tipos de evento para filtro
    from .models import TipoEvento
    tipos_evento = TipoEvento.objects.filter(activo=True)
    
    context = {
        'eventos': eventos,
        'tipos_evento': tipos_evento,
        'filtros_activos': {
            'tipo': tipo_filtro,
            'estado': estado_filtro,
            'q': busqueda,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'orden': orden
        }
    }
    
    return render(request, 'eventos/lista.html', context)


@login_required
def crear_evento(request):
    """Crear nuevo evento (HU-01)"""
    if not request.user.puede_gestionar_eventos():
        messages.error(request, 'No tiene permisos para crear eventos')
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.creado_por = request.user
            evento.save()
            messages.success(request, 'Evento creado exitosamente')
            return redirect('eventos:lista')
    else:
        form = EventoForm()
    
    return render(request, 'eventos/crear.html', {'form': form})


@login_required
def detalle_evento(request, pk):
    """Detalle de evento"""
    evento = get_object_or_404(Evento, pk=pk)
    
    # Check if user is registered and has certificate
    inscripcion_usuario = None
    certificado_usuario = None
    
    if request.user.is_authenticated:
        from inscripciones.models import Inscripcion
        from certificados.models import Certificado
        from django.db.models import Q
        
        inscripcion_usuario = Inscripcion.objects.filter(
            Q(usuario=request.user) | Q(correo=request.user.email),
            evento=evento
        ).first()
        
        if inscripcion_usuario:
            certificado_usuario = Certificado.objects.filter(inscripcion=inscripcion_usuario).first()
    
    return render(request, 'eventos/detalle.html', {
        'evento': evento,
        'inscripcion_usuario': inscripcion_usuario,
        'certificado_usuario': certificado_usuario,
    })



@login_required
def editar_evento(request, pk):
    """Editar evento (HU-02)"""
    evento = get_object_or_404(Evento, pk=pk)
    
    if not request.user.puede_gestionar_eventos():
        messages.error(request, 'No tiene permisos para editar eventos')
        return redirect('eventos:detalle', pk=pk)
    
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.modificado_por = request.user
            evento.save()
            messages.success(request, 'Evento actualizado correctamente')
            return redirect('eventos:detalle', pk=pk)
    else:
        form = EventoForm(instance=evento)
    
    return render(request, 'eventos/editar.html', {'form': form, 'evento': evento})


@login_required
def eliminar_evento(request, pk):
    """Eliminar evento (HU-06)"""
    evento = get_object_or_404(Evento, pk=pk)
    
    if not request.user.es_administrador():
        messages.error(request, 'Solo administradores pueden eliminar eventos')
        return redirect('eventos:detalle', pk=pk)
    
    if request.method == 'POST':
        nombre = evento.nombre
        evento.delete()
        messages.success(request, f'Evento "{nombre}" eliminado correctamente')
        return redirect('eventos:lista')
    
    return render(request, 'eventos/eliminar_confirmar.html', {'evento': evento})


@login_required
def duplicar_evento(request, pk):
    """Duplicar evento (HU-09)"""
    evento = get_object_or_404(Evento, pk=pk)
    
    if not request.user.puede_gestionar_eventos():
        messages.error(request, 'No tiene permisos para duplicar eventos')
        return redirect('eventos:detalle', pk=pk)
    
    nuevo_evento = evento.duplicar(request.user)
    nuevo_evento.save()
    
    messages.success(
        request,
        'Evento duplicado. Por favor actualice las fechas'
    )
    return redirect('eventos:editar', pk=nuevo_evento.id)


@login_required
def publicar_evento(request, pk):
    """Publicar evento"""
    evento = get_object_or_404(Evento, pk=pk)
    
    if not request.user.puede_gestionar_eventos():
        messages.error(request, 'No tiene permisos para publicar eventos')
        return redirect('eventos:detalle', pk=pk)
    
    evento.publicar(request.user)
    messages.success(request, 'Evento publicado correctamente')
    return redirect('eventos:detalle', pk=pk)


@login_required
def cancelar_evento(request, pk):
    """Cancelar evento (HU-23)"""
    evento = get_object_or_404(Evento, pk=pk)
    
    if not request.user.puede_gestionar_eventos():
        messages.error(request, 'No tiene permisos para cancelar eventos')
        return redirect('eventos:detalle', pk=pk)
    
    if request.method == 'POST':
        evento.cancelar(request.user)
        messages.success(request, 'Evento cancelado correctamente')
        
        # TODO: Enviar notificaciones a inscritos
        
        return redirect('eventos:lista')
    
    return render(request, 'eventos/cancelar_confirmar.html', {'evento': evento})
