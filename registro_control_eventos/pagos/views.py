"""
Vistas para la aplicación de Pagos
Placeholder - Implementar según necesidades
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def lista_pagos(request):
    return render(request, 'pagos/lista.html')


@login_required
def registrar_pago(request, inscripcion_id):
    messages.success(request, 'Pago registrado')
    return redirect('pagos:lista')


@login_required
def confirmar_pago(request, pk):
    messages.success(request, 'Pago confirmado')
    return redirect('pagos:lista')


@login_required
def reporte_financiero(request, evento_id):
    return render(request, 'pagos/reporte.html')
