"""
Vistas para generación de reportes
HU-28: Generación de Reportes de Asistencia
HU-29: Exportación de Reportes
HU-30: Panel de Estadísticas Generales
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Count, Sum, Avg
from django.utils import timezone

from eventos.models import Evento
from inscripciones.models import Inscripcion
from asistencias.models import Asistencia
from pagos.models import Pago


@login_required
def dashboard_reportes(request):
    """Dashboard de reportes (HU-30)"""
    if not request.user.puede_gestionar_eventos():
        messages.error(request, 'No tiene permisos')
        return redirect('dashboard:index')
    
    context = {
        'total_eventos': Evento.objects.count(),
        'eventos_activos': Evento.objects.filter(estado='PUBLICADO').count(),
        'total_inscripciones': Inscripcion.objects.filter(estado='CONFIRMADA').count(),
        'total_recaudado': Pago.objects.filter(estado='COMPLETADO').aggregate(Sum('monto'))['monto__sum'] or 0,
    }
    
    return render(request, 'reportes/dashboard.html', context)


@login_required
def reporte_asistencia(request, evento_id):
    """Reporte de asistencia por evento (HU-28)"""
    if not request.user.puede_gestionar_eventos():
        messages.error(request, 'No tiene permisos')
        return redirect('dashboard:index')
    
    evento = get_object_or_404(Evento, pk=evento_id)
    inscripciones = evento.inscripciones.filter(estado='CONFIRMADA')
    
    # Calcular estadísticas
    total_inscritos = inscripciones.count()
    total_asistencias = Asistencia.objects.filter(inscripcion__evento=evento).values('inscripcion').distinct().count()
    porcentaje_asistencia = (total_asistencias / total_inscritos * 100) if total_inscritos > 0 else 0
    
    context = {
        'evento': evento,
        'inscripciones': inscripciones,
        'total_inscritos': total_inscritos,
        'total_asistencias': total_asistencias,
        'porcentaje_asistencia': porcentaje_asistencia,
    }
    
    return render(request, 'reportes/asistencia.html', context)


@login_required
def exportar_reporte_pdf(request, evento_id):
    """Exportar reporte a PDF (HU-29)"""
    if not request.user.puede_gestionar_eventos():
        messages.error(request, 'No tiene permisos')
        return redirect('dashboard:index')
    
    # TODO: Implementar generación de PDF con ReportLab
    messages.info(request, 'Funcionalidad de exportación PDF en desarrollo')
    return redirect('reportes:asistencia', evento_id=evento_id)


@login_required
def exportar_reporte_excel(request, evento_id):
    """Exportar reporte a Excel (HU-29)"""
    if not request.user.puede_gestionar_eventos():
        messages.error(request, 'No tiene permisos')
        return redirect('dashboard:index')
    
    # TODO: Implementar exportación a Excel con openpyxl
    messages.info(request, 'Funcionalidad de exportación Excel en desarrollo')
    return redirect('reportes:asistencia', evento_id=evento_id)

