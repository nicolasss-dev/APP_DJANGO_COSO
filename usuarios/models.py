"""
Modelos para la aplicación de Usuarios
PRCE - Plataforma de Registro y Control de Eventos

HU-11: Creación de Usuarios
HU-12: Asignación de Roles  
HU-13: Edición de Perfil
HU-14: Desactivación de Usuario
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Usuario(AbstractUser):
    """
    Modelo de Usuario personalizado que extiende AbstractUser
    
    Roles:
    - ADMINISTRADOR: Acceso completo al sistema
    - ORGANIZADOR: Puede crear y gestionar eventos
    - ASISTENTE: Puede inscribirse a eventos
    """
    
    ROL_CHOICES = [
        ('ADMINISTRADOR', 'Administrador'),
        ('ORGANIZADOR', 'Organizador'),
        ('ASISTENTE', 'Asistente'),
    ]
    
    # Campos adicionales
    documento = models.CharField(
        max_length=20, 
        unique=True,
        help_text="Número de documento de identidad"
    )
    telefono = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        help_text="Número de teléfono de contacto"
    )
    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default='ASISTENTE',
        help_text="Rol del usuario en el sistema"
    )
    activo = models.BooleanField(
        default=True,
        help_text="Usuario activo en el sistema"
    )
    fecha_desactivacion = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Fecha en que se desactivó el usuario"
    )
    fecha_registro = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha de registro en el sistema"
    )
    ultima_modificacion = models.DateTimeField(
        auto_now=True,
        help_text="Fecha de última modificación del perfil"
    )
    modificado_por = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios_modificados',
        help_text="Usuario que realizó la última modificación"
    )
    intentos_fallidos = models.IntegerField(
        default=0,
        help_text="Contador de intentos fallidos de login"
    )
    bloqueado_hasta = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Fecha hasta la cual está bloqueada la cuenta"
    )
    ultimo_acceso = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Fecha y hora del último acceso al sistema"
    )
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['documento']),
            models.Index(fields=['rol']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"
    
    def save(self, *args, **kwargs):
        """Override save para manejar lógica de negocio"""
        # Si el usuario no está activo y no tiene fecha de desactivación
        if not self.activo and not self.fecha_desactivacion:
            self.fecha_desactivacion = timezone.now()
        # Si el usuario se reactiva, limpiar fecha de desactivación
        elif self.activo and self.fecha_desactivacion:
            self.fecha_desactivacion = None
            self.intentos_fallidos = 0
            self.bloqueado_hasta = None
        
        super().save(*args, **kwargs)
    
    def desactivar(self, usuario_modificador=None):
        """Desactiva el usuario (HU-14)"""
        self.activo = False
        self.fecha_desactivacion = timezone.now()
        self.modificado_por = usuario_modificador
        self.save()
    
    def activar(self, usuario_modificador=None):
        """Activa el usuario (HU-14)"""
        self.activo = True
        self.fecha_desactivacion = None
        self.intentos_fallidos = 0
        self.bloqueado_hasta = None
        self.modificado_por = usuario_modificador
        self.save()
    
    def incrementar_intentos_fallidos(self):
        """
        Incrementa contador de intentos fallidos (HU-04)
        Bloquea la cuenta tras 4 intentos por 15 minutos
        """
        self.intentos_fallidos += 1
        
        if self.intentos_fallidos >= 4:
            from datetime import timedelta
            self.bloqueado_hasta = timezone.now() + timedelta(minutes=15)
        
        self.save()
    
    def resetear_intentos_fallidos(self):
        """Resetea el contador de intentos fallidos"""
        self.intentos_fallidos = 0
        self.bloqueado_hasta = None
        self.save()
    
    def esta_bloqueado(self):
        """Verifica si el usuario está bloqueado temporalmente"""
        if self.bloqueado_hasta:
            return timezone.now() < self.bloqueado_hasta
        return False
    
    def puede_iniciar_sesion(self):
        """Verifica si el usuario puede iniciar sesión"""
        return self.activo and not self.esta_bloqueado()
    
    def registrar_acceso(self):
        """Registra el último acceso del usuario (HU-04)"""
        self.ultimo_acceso = timezone.now()
        self.save(update_fields=['ultimo_acceso'])
    
    def es_administrador(self):
        """Verifica si el usuario es administrador"""
        return self.rol == 'ADMINISTRADOR'
    
    def es_organizador(self):
        """Verifica si el usuario es organizador"""
        return self.rol == 'ORGANIZADOR'
    
    def es_asistente(self):
        """Verifica si el usuario es asistente"""
        return self.rol == 'ASISTENTE'
    
    def puede_gestionar_eventos(self):
        """Verifica si el usuario puede gestionar eventos"""
        return self.rol in ['ADMINISTRADOR', 'ORGANIZADOR']


class HistorialCambioRol(models.Model):
    """
    Modelo para registrar cambios de rol de usuarios (HU-12)
    """
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='historial_roles'
    )
    rol_anterior = models.CharField(max_length=20)
    rol_nuevo = models.CharField(max_length=20)
    fecha_cambio = models.DateTimeField(default=timezone.now)
    cambiado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='cambios_rol_realizados'
    )
    observaciones = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Historial de Cambio de Rol'
        verbose_name_plural = 'Historial de Cambios de Rol'
        ordering = ['-fecha_cambio']
    
    def __str__(self):
        return f"{self.usuario.get_full_name()}: {self.rol_anterior} → {self.rol_nuevo}"
