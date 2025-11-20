"""
Configuración del Admin para la aplicación de Certificados
"""

from django.contrib import admin
from .models import Certificado, PlantillaCertificado


@admin.register(Certificado)
class CertificadoAdmin(admin.ModelAdmin):
    """Admin para Certificado"""
    list_display = [
        'codigo_verificacion', 'inscripcion', 'estado',
        'fecha_generacion', 'fecha_envio', 'intentos_envio'
    ]
    list_filter = ['estado', 'fecha_generacion', 'fecha_envio']
    search_fields = [
        'codigo_verificacion',
        'inscripcion__nombre',
        'inscripcion__apellido',
        'inscripcion__documento'
    ]
    readonly_fields = ['codigo_verificacion', 'fecha_generacion', 'intentos_envio']
    date_hierarchy = 'fecha_generacion'
    
    fieldsets = (
        ('Información', {
            'fields': ('inscripcion', 'codigo_verificacion')
        }),
        ('Archivo', {
            'fields': ('archivo_pdf',)
        }),
        ('Estado', {
            'fields': ('estado', 'fecha_generacion', 'fecha_envio', 'intentos_envio')
        }),
        ('Errores', {
            'fields': ('error_envio',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['generar_pdfs', 'enviar_certificados', 'reenviar_certificados']
    
    def generar_pdfs(self, request, queryset):
        """Acción para generar PDFs de certificados seleccionados"""
        count = 0
        for certificado in queryset:
            if not certificado.archivo_pdf:
                certificado.generar_pdf()
                count += 1
        self.message_user(request, f"{count} PDF(s) generado(s) correctamente.")
    generar_pdfs.short_description = "Generar PDFs de certificados"
    
    def enviar_certificados(self, request, queryset):
        """Acción para enviar certificados por correo"""
        exitosos = 0
        fallidos = 0
        for certificado in queryset:
            if certificado.enviar_por_correo():
                exitosos += 1
            else:
                fallidos += 1
        self.message_user(
            request,
            f"Enviados: {exitosos}, Fallidos: {fallidos}"
        )
    enviar_certificados.short_description = "Enviar certificados por correo"
    
    def reenviar_certificados(self, request, queryset):
        """Acción para reenviar certificados con error"""
        queryset_con_error = queryset.filter(estado='ERROR')
        exitosos = 0
        for certificado in queryset_con_error:
            if certificado.enviar_por_correo():
                exitosos += 1
        self.message_user(
            request,
            f"{exitosos} certificado(s) reenviado(s) exitosamente."
        )
    reenviar_certificados.short_description = "Reenviar certificados con error"


@admin.register(PlantillaCertificado)
class PlantillaCertificadoAdmin(admin.ModelAdmin):
    """Admin para PlantillaCertificado"""
    list_display = ['nombre', 'activa', 'fecha_creacion', 'creada_por']
    list_filter = ['activa', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['fecha_creacion']
    
    fieldsets = (
        ('Información', {
            'fields': ('nombre', 'descripcion', 'activa')
        }),
        ('Diseño', {
            'fields': ('logo', 'color_primario', 'color_secundario')
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'creada_por'),
            'classes': ('collapse',)
        }),
    )
