"""
Vistas para el Dashboard
HU-28: Generación de Reportes de Asistencia
HU-30: Panel de Estadísticas Generales
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta

from eventos.models import Evento
from inscripciones.models import Inscripcion
from pagos.models import Pago
from asistencias.models import Asistencia


@login_required
def dashboard_view(request):
    """
    Dashboard principal con estadísticas (HU-30)
    """
    user = request.user
    
    # Inicializar variables para evitar errores de scope
    proximos_eventos = []
    eventos_disponibles = []
    actividad_reciente = []
    
    # Estadísticas generales
    stats = {
        'total_eventos': 0,
        'total_inscripciones': 0,
        'total_recaudado': 0,
        'promedio_asistencia': 0,
    }
    
    # Calcular estadísticas según el rol
    if user.es_administrador() or user.es_organizador():
        # Eventos
        eventos_query = Evento.objects.all()
        if user.es_organizador() and not user.es_administrador():
            eventos_query = eventos_query.filter(creado_por=user)
        
        stats['total_eventos'] = eventos_query.count()
        
        # Inscripciones
        stats['total_inscripciones'] = Inscripcion.objects.filter(
            evento__in=eventos_query,
            estado='CONFIRMADA'
        ).count()
        
        # Recaudado
        total_recaudado = Pago.objects.filter(
            inscripcion__evento__in=eventos_query,
            estado='COMPLETADO'
        ).aggregate(total=Sum('monto'))['total'] or 0
        stats['total_recaudado'] = total_recaudado
        
        # Promedio de asistencia
        # Eventos finalizados
        eventos_finalizados = eventos_query.filter(estado='FINALIZADO')
        if eventos_finalizados.exists():
            promedios = []
            for evento in eventos_finalizados:
                total_inscritos = evento.inscripciones.filter(estado='CONFIRMADA').count()
                if total_inscritos > 0:
                    total_asistencias = evento.inscripciones.filter(
                        estado='CONFIRMADA',
                        asistencias__isnull=False
                    ).distinct().count()
                    promedio_evento = (total_asistencias / total_inscritos) * 100
                    promedios.append(promedio_evento)
            
            if promedios:
                stats['promedio_asistencia'] = sum(promedios) / len(promedios)
        
        # Próximos eventos - CORREGIDO
        proximos_eventos = eventos_query.filter(
            fecha_inicio__gte=timezone.now(),
            estado__in=['PUBLICADO', 'EN_CURSO']
        ).select_related('tipo_evento', 'creado_por').order_by('fecha_inicio')[:5]
        
        # Actividad reciente (solo administradores)
        if user.es_administrador():
            # Últimas inscripciones
            ultimas_inscripciones = Inscripcion.objects.select_related(
                'evento', 'usuario'
            ).order_by('-fecha_inscripcion')[:10]
            
            for inscripcion in ultimas_inscripciones:
                actividad_reciente.append({
                    'usuario': inscripcion.get_nombre_completo(),
                    'accion': f'se inscribió a {inscripcion.evento.nombre}',
                    'fecha': inscripcion.fecha_inscripcion
                })
        
    else:
        # Asistente: ver solo sus propias inscripciones
        stats['total_inscripciones'] = Inscripcion.objects.filter(
            Q(usuario=user) | Q(correo=user.email),
            estado='CONFIRMADA'
        ).count()
        
        # Eventos en los que está inscrito
        eventos_inscritos = Evento.objects.filter(
            Q(inscripciones__usuario=user) | Q(inscripciones__correo=user.email),
            fecha_inicio__gte=timezone.now(),
            estado__in=['PUBLICADO', 'EN_CURSO']
        ).distinct().select_related('tipo_evento').order_by('fecha_inicio')[:5]
        
        # Eventos disponibles para inscribirse (no inscrito aún)
        eventos_disponibles = Evento.objects.filter(
            estado='PUBLICADO',
            fecha_inicio__gte=timezone.now()
        ).exclude(
            Q(inscripciones__usuario=user) | Q(inscripciones__correo=user.email)
        ).select_related('tipo_evento').order_by('fecha_inicio')[:10]
        
        proximos_eventos = eventos_inscritos
    
    context = {
        'stats': stats,
        'proximos_eventos': proximos_eventos,
        'actividad_reciente': actividad_reciente,
    }
    
    # Agregar eventos disponibles para asistentes
    if not (user.es_administrador() or user.es_organizador()):
        context['eventos_disponibles'] = eventos_disponibles
    
    return render(request, 'dashboard/index.html', context)