"""
Vistas para la aplicación de Certificados
Placeholder - Implementar según necesidades
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def lista_certificados(request):
    return render(request, 'certificados/lista.html')


@login_required
def generar_masivo(request):
    messages.success(request, 'Certificados generados')
    return redirect('certificados:lista')


@login_required
def generar_certificado(request, inscripcion_id):
    messages.success(request, 'Certificado generado')
    return redirect('certificados:lista')


@login_required
def enviar_certificado(request, certificado_id):
    messages.success(request, 'Certificado enviado')
    return redirect('certificados:lista')


def verificar_certificado(request, codigo):
    return render(request, 'certificados/verificar.html')
