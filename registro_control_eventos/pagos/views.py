"""
Vistas para la aplicación de Pagos
PRCE - Plataforma de Registro y Control de Eventos

HU-25: Registro Manual de Pagos
HU-26: Integración con Pasarela de Pagos (SIMULADA)
HU-27: Reporte Financiero por Evento
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.urls import reverse
from decimal import Decimal
import time
import uuid

from .models import Pago, MetodoPago, ConfiguracionPasarela
from .forms import (
    PagoEfectivoForm, 
    PagoTransferenciaForm, 
    PagoTarjetaForm, 
    PagoPasarelaForm,
    ConfirmarPagoForm
)
from inscripciones.models import Inscripcion
from eventos.models import Evento


@login_required
def lista_pagos(request):
    """Lista todos los pagos con filtros"""
    # Verificar permisos
    if not request.user.puede_gestionar_eventos():
        messages.error(request, 'No tiene permisos para ver esta página')
        return redirect('dashboard:index')
    
    # Obtener filtros
    estado = request.GET.get('estado', '')
    metodo = request.GET.get('metodo', '')
    evento_id = request.GET.get('evento', '')
    
    # Query base
    pagos = Pago.objects.select_related('inscripcion', 'inscripcion__evento', 'metodo_pago').all()
    
    # Aplicar filtros
    if estado:
        pagos = pagos.filter(estado=estado)
    if metodo:
        pagos = pagos.filter(metodo_pago__codigo=metodo)
    if evento_id:
        pagos = pagos.filter(inscripcion__evento_id=evento_id)
    
    # Estadísticas
    total_pagos = pagos.count()
    total_monto = pagos.filter(estado='COMPLETADO').aggregate(Sum('monto'))['monto__sum'] or Decimal('0.00')
    pendientes = pagos.filter(estado='PENDIENTE').count()
    
    context = {
        'pagos': pagos.order_by('-fecha_pago'),
        'metodos_pago': MetodoPago.objects.filter(activo=True),
        'eventos': Evento.objects.all(),
        'total_pagos': total_pagos,
        'total_monto': total_monto,
        'pendientes': pendientes,
        'estado_filter': estado,
        'metodo_filter': metodo,
        'evento_filter': evento_id,
    }
    
    return render(request, 'pagos/lista.html', context)


@login_required
def seleccionar_metodo_pago(request, inscripcion_id):
    """Vista para seleccionar método de pago"""
    inscripcion = get_object_or_404(Inscripcion, pk=inscripcion_id)
    
    # Verificar que la inscripción esté pendiente de pago
    if inscripcion.pago_confirmado:
        messages.warning(request, 'Esta inscripción ya tiene un pago confirmado')
        return redirect('inscripciones:detalle', pk=inscripcion_id)
    
    # Obtener métodos de pago activos
    metodos_pago = MetodoPago.objects.filter(activo=True)
    pasarelas = ConfiguracionPasarela.objects.filter(activa=True)
    
    context = {
        'inscripcion': inscripcion,
        'metodos_pago': metodos_pago,
        'pasarelas': pasarelas,
        'monto': inscripcion.evento.costo,
    }
    
    return render(request, 'pagos/seleccionar_metodo.html', context)


@login_required
def procesar_pago_efectivo(request, inscripcion_id):
    """Procesar pago en efectivo"""
    inscripcion = get_object_or_404(Inscripcion, pk=inscripcion_id)
    metodo = get_object_or_404(MetodoPago, codigo='EFECTIVO')
    
    if request.method == 'POST':
        form = PagoEfectivoForm(request.POST)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.inscripcion = inscripcion
            pago.metodo_pago = metodo
            pago.estado = 'COMPLETADO'  # Efectivo se considera completado inmediatamente
            pago.registrado_por = request.user
            pago.save()
            
            # Actualizar inscripción
            inscripcion.pago_confirmado = True
            inscripcion.fecha_confirmacion = timezone.now()
            inscripcion.estado = 'CONFIRMADA'
            inscripcion.save()
            
            # Enviar notificación (simulada)
            pago.enviar_notificacion_confirmacion()
            
            messages.success(request, '✓ Pago en efectivo registrado exitosamente')
            return redirect('pagos:confirmacion', pago_id=pago.id)
    else:
        form = PagoEfectivoForm(initial={'monto': inscripcion.evento.costo})
    
    context = {
        'form': form,
        'inscripcion': inscripcion,
        'metodo': metodo,
    }
    
    return render(request, 'pagos/form_efectivo.html', context)


@login_required
def procesar_pago_transferencia(request, inscripcion_id):
    """Procesar pago por transferencia bancaria"""
    inscripcion = get_object_or_404(Inscripcion, pk=inscripcion_id)
    metodo = get_object_or_404(MetodoPago, codigo='TRANSFERENCIA')
    
    if request.method == 'POST':
        form = PagoTransferenciaForm(request.POST, request.FILES)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.inscripcion = inscripcion
            pago.metodo_pago = metodo
            pago.estado = 'PENDIENTE'  # Transferencias requieren verificación
            pago.registrado_por = request.user
            
            # Guardar comprobante si se subió
            if 'comprobante' in request.FILES:
                pago.comprobante = request.FILES['comprobante']
            
            pago.save()
            
            messages.success(request, '✓ Transferencia registrada. Pendiente de verificación.')
            return redirect('pagos:confirmacion', pago_id=pago.id)
    else:
        form = PagoTransferenciaForm(initial={'monto': inscripcion.evento.costo})
    
    context = {
        'form': form,
        'inscripcion': inscripcion,
        'metodo': metodo,
    }
    
    return render(request, 'pagos/form_transferencia.html', context)


@login_required
def procesar_pago_tarjeta(request, inscripcion_id):
    """Procesar pago con tarjeta (SIMULADO)"""
    inscripcion = get_object_or_404(Inscripcion, pk=inscripcion_id)
    metodo = get_object_or_404(MetodoPago, codigo='TARJETA')
    
    if request.method == 'POST':
        form = PagoTarjetaForm(request.POST)
        if form.is_valid():
            # SIMULACIÓN: Guardar el pago
            pago = form.save(commit=False)
            pago.inscripcion = inscripcion
            pago.metodo_pago = metodo
            pago.estado = 'COMPLETADO'
            pago.registrado_por = request.user
            
            # Generar ID de transacción simulado
            pago.pasarela_transaccion_id = f"SIM-{uuid.uuid4().hex[:12].upper()}"
            
            pago.save()
            
            # Actualizar inscripción
            inscripcion.pago_confirmado = True
            inscripcion.fecha_confirmacion = timezone.now()
            inscripcion.estado = 'CONFIRMADA'
            inscripcion.save()
            
            # Enviar notificación (simulada)
            pago.enviar_notificacion_confirmacion()
            
            messages.success(request, '✓ Pago con tarjeta procesado exitosamente')
            return redirect('pagos:confirmacion', pago_id=pago.id)
    else:
        form = PagoTarjetaForm(initial={'monto': inscripcion.evento.costo})
    
    context = {
        'form': form,
        'inscripcion': inscripcion,
        'metodo': metodo,
    }
    
    return render(request, 'pagos/form_tarjeta.html', context)


@login_required
def procesar_pago_pasarela(request, inscripcion_id):
    """Iniciar procesamiento con pasarela de pago (SIMULADO)"""
    inscripcion = get_object_or_404(Inscripcion, pk=inscripcion_id)
    metodo = get_object_or_404(MetodoPago, codigo='PASARELA')
    
    if request.method == 'POST':
        form = PagoPasarelaForm(request.POST)
        if form.is_valid():
            pasarela = form.cleaned_data['pasarela']
            email = form.cleaned_data['email_confirmacion']
            
            # Crear registro de pago pendiente
            pago = Pago.objects.create(
                inscripcion=inscripcion,
                metodo_pago=metodo,
                monto=inscripcion.evento.costo,
                estado='PENDIENTE',
                registrado_por=request.user,
                referencia=f"PASARELA-{pasarela.nombre}-{uuid.uuid4().hex[:8].upper()}",
                datos_pasarela={
                    'pasarela': pasarela.nombre,
                    'email_confirmacion': email,
                }
            )
            
            # Redirigir a página de simulación de pasarela
            return redirect('pagos:simulacion_pasarela', pago_id=pago.id)
    else:
        form = PagoPasarelaForm(initial={
            'email_confirmacion': inscripcion.correo
        })
    
    context = {
        'form': form,
        'inscripcion': inscripcion,
        'metodo': metodo,
    }
    
    return render(request, 'pagos/form_pasarela.html', context)


def simulacion_pasarela(request, pago_id):
    """Página de simulación de pasarela de pago"""
    pago = get_object_or_404(Pago, pk=pago_id)
    
    context = {
        'pago': pago,
        'pasarela_nombre': pago.datos_pasarela.get('pasarela', 'Pasarela'),
    }
    
    return render(request, 'pagos/simulacion_pasarela.html', context)


def callback_pasarela(request, pago_id):
    """Callback simulado de pasarela de pago"""
    pago = get_object_or_404(Pago, pk=pago_id)
    
    # SIMULACIÓN: Marcar como exitoso
    resultado = request.GET.get('resultado', 'exito')
    
    if resultado == 'exito':
        pago.estado = 'COMPLETADO'
        pago.pasarela_transaccion_id = f"SIM-TRX-{uuid.uuid4().hex[:16].upper()}"
        pago.save()
        
        # Actualizar inscripción
        inscripcion = pago.inscripcion
        inscripcion.pago_confirmado = True
        inscripcion.fecha_confirmacion = timezone.now()
        inscripcion.estado = 'CONFIRMADA'
        inscripcion.save()
        
        # Enviar notificación (simulada)
        pago.enviar_notificacion_confirmacion()
        
        messages.success(request, '✓ ¡Pago procesado exitosamente!')
    else:
        pago.estado = 'RECHAZADO'
        pago.save()
        messages.error(request, '✗ El pago fue rechazado. Intente nuevamente.')
    
    return redirect('pagos:confirmacion', pago_id=pago.id)


@login_required
def confirmacion_pago(request, pago_id):
    """Página de confirmación después del pago"""
    pago = get_object_or_404(Pago, pk=pago_id)
    
    context = {
        'pago': pago,
    }
    
    return render(request, 'pagos/confirmacion.html', context)


@login_required
def detalle_pago(request, pago_id):
    """Ver detalles de un pago"""
    pago = get_object_or_404(Pago, pk=pago_id)
    
    context = {
        'pago': pago,
    }
    
    return render(request, 'pagos/detalle.html', context)


@login_required
def confirmar_pago_manual(request, pago_id):
    """Confirmar o rechazar un pago manualmente"""
    if not request.user.puede_gestionar_eventos():
        messages.error(request, 'No tiene permisos')
        return redirect('dashboard:index')
    
    pago = get_object_or_404(Pago, pk=pago_id)
    
    if request.method == 'POST':
        form = ConfirmarPagoForm(request.POST)
        if form.is_valid():
            accion = form.cleaned_data['accion']
            notas = form.cleaned_data.get('notas', '')
            
            if accion == 'CONFIRMAR':
                pago.confirmar(usuario=request.user)
                messages.success(request, '✓ Pago confirmado exitosamente')
            else:
                pago.rechazar(motivo=notas)
                messages.warning(request, 'Pago rechazado')
            
            return redirect('pagos:detalle', pago_id=pago.id)
    else:
        form = ConfirmarPagoForm()
    
    context = {
        'pago': pago,
        'form': form,
    }
    
    return render(request, 'pagos/confirmar_manual.html', context)


@login_required
def reporte_financiero(request, evento_id):
    """Reporte financiero de un evento (HU-27)"""
    if not request.user.puede_gestionar_eventos():
        messages.error(request, 'No tiene permisos')
        return redirect('dashboard:index')
    
    evento = get_object_or_404(Evento, pk=evento_id)
    reporte = Pago.obtener_reporte_evento(evento)
    
    context = {
        'evento': evento,
        'reporte': reporte,
    }
    
    return render(request, 'pagos/reporte.html', context)
