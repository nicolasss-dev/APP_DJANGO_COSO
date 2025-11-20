"""
Configuración del Admin para la aplicación de Usuarios
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, HistorialCambioRol


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Configuración personalizada del Admin para el modelo Usuario
    """
    list_display = ['username', 'email', 'get_full_name', 'rol', 'activo', 'fecha_registro']
    list_filter = ['rol', 'activo', 'fecha_registro']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'documento']
    ordering = ['-fecha_registro']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('documento', 'telefono', 'rol', 'activo', 'fecha_desactivacion')
        }),
        ('Seguimiento', {
            'fields': ('fecha_registro', 'ultima_modificacion', 'modificado_por', 'ultimo_acceso')
        }),
        ('Seguridad', {
            'fields': ('intentos_fallidos', 'bloqueado_hasta')
        }),
    )
    
    readonly_fields = ['fecha_registro', 'ultima_modificacion', 'ultimo_acceso']
    
    actions = ['activar_usuarios', 'desactivar_usuarios']
    
    def activar_usuarios(self, request, queryset):
        """Acción para activar usuarios seleccionados"""
        for usuario in queryset:
            usuario.activar(usuario_modificador=request.user)
        self.message_user(request, f"{queryset.count()} usuarios activados correctamente.")
    activar_usuarios.short_description = "Activar usuarios seleccionados"
    
    def desactivar_usuarios(self, request, queryset):
        """Acción para desactivar usuarios seleccionados"""
        for usuario in queryset:
            usuario.desactivar(usuario_modificador=request.user)
        self.message_user(request, f"{queryset.count()} usuarios desactivados correctamente.")
    desactivar_usuarios.short_description = "Desactivar usuarios seleccionados"


@admin.register(HistorialCambioRol)
class HistorialCambioRolAdmin(admin.ModelAdmin):
    """
    Configuración del Admin para el historial de cambios de rol
    """
    list_display = ['usuario', 'rol_anterior', 'rol_nuevo', 'fecha_cambio', 'cambiado_por']
    list_filter = ['fecha_cambio', 'rol_anterior', 'rol_nuevo']
    search_fields = ['usuario__username', 'usuario__email', 'observaciones']
    readonly_fields = ['fecha_cambio']
    ordering = ['-fecha_cambio']
