"""
Configuración del Admin para la aplicación de Notificaciones
"""

from django.contrib import admin
from .models import TipoNotificacion, PlantillaCorreo, Notificacion, ConfiguracionRecordatorio


@admin.register(TipoNotificacion)
class TipoNotificacionAdmin(admin.ModelAdmin):
    """Admin para TipoNotificacion"""
    list_display = ['get_codigo_display', 'nombre', 'activo']
    list_filter = ['activo']
    search_fields = ['codigo', 'nombre', 'descripcion']


@admin.register(PlantillaCorreo)
class PlantillaCorreoAdmin(admin.ModelAdmin):
    """Admin para PlantillaCorreo"""
    list_display = [
        'tipo_notificacion', 'nombre', 'activa',
        'predeterminada', 'fecha_creacion'
    ]
    list_filter = ['activa', 'predeterminada', 'tipo_notificacion']
    search_fields = ['nombre', 'asunto']
    readonly_fields = ['fecha_creacion']
    
    fieldsets = (
        ('Información', {
            'fields': ('tipo_notificacion', 'nombre', 'activa', 'predeterminada')
        }),
        ('Contenido', {
            'fields': ('asunto', 'cuerpo_texto', 'cuerpo_html', 'pie_pagina')
        }),
        ('Variables', {
            'fields': ('variables_disponibles',),
            'description': 'Variables que puedes usar en las plantillas'
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'creada_por'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    """Admin para Notificacion"""
    list_display = [
        'tipo_notificacion', 'destinatario_email', 'asunto',
        'estado', 'fecha_programada', 'fecha_envio', 'intentos'
    ]
    list_filter = ['estado', 'tipo_notificacion', 'fecha_programada']
    search_fields = ['destinatario_email', 'destinatario_nombre', 'asunto']
    readonly_fields = ['fecha_envio', 'intentos']
    date_hierarchy = 'fecha_programada'
    
    fieldsets = (
        ('Tipo y Destinatario', {
            'fields': ('tipo_notificacion', 'destinatario_email', 'destinatario_nombre')
        }),
        ('Contenido', {
            'fields': ('asunto', 'cuerpo')
        }),
        ('Estado', {
            'fields': ('estado', 'fecha_programada', 'fecha_envio', 'intentos')
        }),
        ('Relaciones', {
            'fields': ('evento', 'inscripcion'),
            'classes': ('collapse',)
        }),
        ('Errores', {
            'fields': ('error_mensaje',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['enviar_notificaciones', 'reenviar_con_error']
    
    def enviar_notificaciones(self, request, queryset):
        """Acción para enviar notificaciones pendientes"""
        exitosos = 0
        fallidos = 0
        for notificacion in queryset.filter(estado='PENDIENTE'):
            if notificacion.enviar():
                exitosos += 1
            else:
                fallidos += 1
        self.message_user(
            request,
            f"Enviados: {exitosos}, Fallidos: {fallidos}"
        )
    enviar_notificaciones.short_description = "Enviar notificaciones seleccionadas"
    
    def reenviar_con_error(self, request, queryset):
        """Acción para reenviar notificaciones con error"""
        exitosos = 0
        for notificacion in queryset.filter(estado='ERROR'):
            if notificacion.enviar():
                exitosos += 1
        self.message_user(
            request,
            f"{exitosos} notificación(es) reenviada(s) exitosamente."
        )
    reenviar_con_error.short_description = "Reenviar notificaciones con error"


@admin.register(ConfiguracionRecordatorio)
class ConfiguracionRecordatorioAdmin(admin.ModelAdmin):
    """Admin para ConfiguracionRecordatorio"""
    list_display = [
        'evento', 'activo', 'horas_antes',
        'enviado', 'fecha_envio'
    ]
    list_filter = ['activo', 'enviado']
    search_fields = ['evento__nombre']
    readonly_fields = ['fecha_envio']
