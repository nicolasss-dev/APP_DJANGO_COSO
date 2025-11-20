"""
Vistas para la aplicación de Notificaciones
Placeholder - Implementar según necesidades
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def lista_notificaciones(request):
    return render(request, 'notificaciones/lista.html')


@login_required
def lista_plantillas(request):
    return render(request, 'notificaciones/plantillas.html')


@login_required
def enviar_notificacion(request):
    messages.success(request, 'Notificación enviada')
    return redirect('notificaciones:lista')
