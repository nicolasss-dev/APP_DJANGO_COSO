"""
Vistas para la aplicación de Asistencias
Placeholder - Implementar según necesidades
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def lista_asistencias(request):
    return render(request, 'asistencias/lista.html')


@login_required
def control_asistencias(request):
    return render(request, 'asistencias/control.html')


@login_required
def registrar_asistencia(request, inscripcion_id):
    messages.success(request, 'Asistencia registrada')
    return redirect('asistencias:control')


def registrar_qr(request, codigo_qr):
    return render(request, 'asistencias/qr.html')


@login_required
def asistencias_evento(request, evento_id):
    return render(request, 'asistencias/evento.html')
