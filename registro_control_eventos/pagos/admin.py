"""
Configuración del Admin para la aplicación de Pagos
"""

from django.contrib import admin
from .models import MetodoPago, Pago


@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    """Admin para MetodoPago"""
    list_display = ['get_codigo_display', 'nombre', 'activo', 'requiere_comprobante']
    list_filter = ['activo', 'requiere_comprobante']
    search_fields = ['nombre', 'descripcion']


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    """Admin para Pago"""
    list_display = [
        'id', 'inscripcion', 'monto', 'metodo_pago',
        'estado', 'fecha_pago', 'referencia'
    ]
    list_filter = ['estado', 'metodo_pago', 'fecha_pago']
    search_fields = [
        'inscripcion__nombre',
        'inscripcion__apellido',
        'referencia',
        'pasarela_transaccion_id'
    ]
    readonly_fields = ['fecha_confirmacion', 'pasarela_respuesta']
    date_hierarchy = 'fecha_pago'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('inscripcion', 'monto', 'metodo_pago', 'referencia')
        }),
        ('Estado', {
            'fields': ('estado', 'fecha_pago', 'fecha_confirmacion')
        }),
        ('Comprobante', {
            'fields': ('comprobante',)
        }),
        ('Registro', {
            'fields': ('registrado_por', 'notas')
        }),
        ('Datos de Pasarela', {
            'fields': ('pasarela_transaccion_id', 'pasarela_respuesta'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['confirmar_pagos', 'rechazar_pagos']
    
    def confirmar_pagos(self, request, queryset):
        """Acción para confirmar pagos seleccionados"""
        for pago in queryset.filter(estado='PENDIENTE'):
            pago.confirmar(usuario=request.user)
        self.message_user(request, f"{queryset.count()} pago(s) confirmado(s).")
    confirmar_pagos.short_description = "Confirmar pagos seleccionados"
    
    def rechazar_pagos(self, request, queryset):
        """Acción para rechazar pagos seleccionados"""
        for pago in queryset.filter(estado='PENDIENTE'):
            pago.rechazar()
        self.message_user(request, f"{queryset.count()} pago(s) rechazado(s).")
    rechazar_pagos.short_description = "Rechazar pagos seleccionados"



