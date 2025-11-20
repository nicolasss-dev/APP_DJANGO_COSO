"""
Configuración del Admin para la aplicación de Inscripciones
"""

from django.contrib import admin
from .models import Inscripcion, RegistroMasivo


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    """Admin para Inscripcion"""
    list_display = [
        'get_nombre_completo', 'evento', 'correo', 'telefono',
        'estado', 'fecha_inscripcion', 'porcentaje_asistencia'
    ]
    list_filter = ['estado', 'evento', 'fecha_inscripcion', 'registro_masivo']
    search_fields = ['nombre', 'apellido', 'documento', 'correo']
    readonly_fields = ['codigo_qr', 'fecha_inscripcion', 'fecha_confirmacion', 'porcentaje_asistencia']
    date_hierarchy = 'fecha_inscripcion'
    
    fieldsets = (
        ('Información del Evento', {
            'fields': ('evento', 'usuario')
        }),
        ('Datos del Participante', {
            'fields': ('nombre', 'apellido', 'documento', 'correo', 'telefono')
        }),
        ('Estado', {
            'fields': ('estado', 'pago_confirmado', 'fecha_confirmacion')
        }),
        ('Código QR', {
            'fields': ('codigo_qr',)
        }),
        ('Seguimiento', {
            'fields': ('fecha_inscripcion', 'porcentaje_asistencia', 'registro_masivo', 'notas')
        }),
    )
    
    actions = ['confirmar_inscripciones', 'cancelar_inscripciones']
    
    def confirmar_inscripciones(self, request, queryset):
        """Acción para confirmar inscripciones"""
        for inscripcion in queryset:
            inscripcion.confirmar()
        self.message_user(request, f"{queryset.count()} inscripción(es) confirmada(s).")
    confirmar_inscripciones.short_description = "Confirmar inscripciones seleccionadas"
    
    def cancelar_inscripciones(self, request, queryset):
        """Acción para cancelar inscripciones"""
        for inscripcion in queryset:
            inscripcion.cancelar()
        self.message_user(request, f"{queryset.count()} inscripción(es) cancelada(s).")
    cancelar_inscripciones.short_description = "Cancelar inscripciones seleccionadas"


@admin.register(RegistroMasivo)
class RegistroMasivoAdmin(admin.ModelAdmin):
    """Admin para RegistroMasivo"""
    list_display = [
        'evento', 'fecha_carga', 'cargado_por',
        'total_registros', 'registros_exitosos', 'registros_fallidos'
    ]
    list_filter = ['fecha_carga', 'evento']
    search_fields = ['evento__nombre']
    readonly_fields = ['fecha_carga', 'total_registros', 'registros_exitosos', 'registros_fallidos']
    date_hierarchy = 'fecha_carga'
