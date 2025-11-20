"""
Configuración del Admin para la aplicación de Eventos
"""

from django.contrib import admin
from .models import Evento, TipoEvento, HistorialCambioEvento


@admin.register(TipoEvento)
class TipoEventoAdmin(admin.ModelAdmin):
    """Admin para TipoEvento"""
    list_display = ['nombre', 'color_badge', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'descripcion']


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    """Admin para Evento"""
    list_display = [
        'nombre', 'tipo_evento', 'fecha_inicio', 'fecha_fin',
        'estado', 'cupo_maximo', 'total_inscritos', 'costo'
    ]
    list_filter = ['estado', 'tipo_evento', 'fecha_inicio', 'genera_certificado']
    search_fields = ['nombre', 'descripcion', 'lugar']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por']
    date_hierarchy = 'fecha_inicio'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'tipo_evento', 'estado')
        }),
        ('Fecha y Lugar', {
            'fields': ('fecha_inicio', 'fecha_fin', 'lugar', 'direccion')
        }),
        ('Capacidad y Costo', {
            'fields': ('cupo_maximo', 'costo')
        }),
        ('Imagen Promocional', {
            'fields': ('imagen_banner',)
        }),
        ('Configuración', {
            'fields': (
                'requiere_aprobacion', 'genera_certificado',
                'porcentaje_asistencia_minimo', 'numero_sesiones'
            )
        }),
        ('Auditoría', {
            'fields': (
                'creado_por', 'fecha_creacion',
                'modificado_por', 'fecha_modificacion'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['publicar_eventos', 'cancelar_eventos', 'finalizar_eventos']
    
    def publicar_eventos(self, request, queryset):
        """Acción para publicar eventos"""
        count = 0
        for evento in queryset:
            if evento.estado == 'BORRADOR':
                evento.publicar(request.user)
                count += 1
        self.message_user(request, f"{count} evento(s) publicado(s) correctamente.")
    publicar_eventos.short_description = "Publicar eventos seleccionados"
    
    def cancelar_eventos(self, request, queryset):
        """Acción para cancelar eventos"""
        for evento in queryset:
            evento.cancelar(request.user)
        self.message_user(request, f"{queryset.count()} evento(s) cancelado(s) correctamente.")
    cancelar_eventos.short_description = "Cancelar eventos seleccionados"
    
    def finalizar_eventos(self, request, queryset):
        """Acción para finalizar eventos"""
        for evento in queryset:
            evento.finalizar(request.user)
        self.message_user(request, f"{queryset.count()} evento(s) finalizado(s) correctamente.")
    finalizar_eventos.short_description = "Finalizar eventos seleccionados"


@admin.register(HistorialCambioEvento)
class HistorialCambioEventoAdmin(admin.ModelAdmin):
    """Admin para HistorialCambioEvento"""
    list_display = ['evento', 'campo_modificado', 'fecha_cambio', 'modificado_por']
    list_filter = ['campo_modificado', 'fecha_cambio']
    search_fields = ['evento__nombre']
    readonly_fields = ['fecha_cambio']
    ordering = ['-fecha_cambio']
