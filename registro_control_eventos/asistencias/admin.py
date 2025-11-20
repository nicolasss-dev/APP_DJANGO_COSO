"""
Configuración del Admin para la aplicación de Asistencias
"""

from django.contrib import admin
from .models import Asistencia, ControlAsistencia


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    """Admin para Asistencia"""
    list_display = [
        'inscripcion', 'sesion', 'fecha_registro',
        'metodo_registro', 'registrado_por'
    ]
    list_filter = ['metodo_registro', 'fecha_registro', 'sesion']
    search_fields = [
        'inscripcion__nombre',
        'inscripcion__apellido',
        'inscripcion__documento'
    ]
    readonly_fields = ['fecha_registro', 'ip_address', 'user_agent']
    date_hierarchy = 'fecha_registro'
    
    fieldsets = (
        ('Información', {
            'fields': ('inscripcion', 'sesion', 'fecha_registro')
        }),
        ('Método de Registro', {
            'fields': ('metodo_registro', 'registrado_por')
        }),
        ('Datos de Verificación', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Observaciones', {
            'fields': ('notas',)
        }),
    )


@admin.register(ControlAsistencia)
class ControlAsistenciaAdmin(admin.ModelAdmin):
    """Admin para ControlAsistencia"""
    list_display = [
        'evento', 'sesion', 'fecha_sesion',
        'total_asistentes', 'total_inscritos',
        'porcentaje_asistencia', 'activo'
    ]
    list_filter = ['activo', 'fecha_sesion', 'evento']
    search_fields = ['evento__nombre']
    readonly_fields = ['fecha_creacion', 'total_asistentes', 'total_inscritos', 'porcentaje_asistencia']
    date_hierarchy = 'fecha_sesion'
