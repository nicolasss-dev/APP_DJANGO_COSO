"""
Modelos para la aplicación de Inscripciones
PRCE - Plataforma de Registro y Control de Eventos

HU-03: Registro de Asistentes
HU-10: Registro Masivo de Asistentes
"""

from django.db import models
from django.utils import timezone
from django.core.validators import EmailValidator
from eventos.models import Evento
from usuarios.models import Usuario
import uuid


class Inscripcion(models.Model):
    """
    Modelo de Inscripción a eventos
    """
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('CANCELADA', 'Cancelada'),
        ('RECHAZADA', 'Rechazada'),
    ]
    
    # Relaciones
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name='inscripciones',
        help_text="Evento al que se inscribe"
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='inscripciones',
        help_text="Usuario registrado (si aplica)"
    )
    
    # Datos del participante (para inscripciones públicas sin cuenta)
    nombre = models.CharField(
        max_length=100,
        help_text="Nombre del participante"
    )
    apellido = models.CharField(
        max_length=100,
        help_text="Apellido del participante"
    )
    documento = models.CharField(
        max_length=20,
        help_text="Número de documento"
    )
    correo = models.EmailField(
        validators=[EmailValidator()],
        help_text="Correo electrónico"
    )
    telefono = models.CharField(
        max_length=15,
        help_text="Teléfono de contacto"
    )
    
    # Estado y seguimiento
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE',
        help_text="Estado de la inscripción"
    )
    fecha_inscripcion = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha y hora de inscripción"
    )
    
    # Código QR único para registro de asistencia (HU-17)
    codigo_qr = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Código único para QR de asistencia"
    )
    
    # Confirmación de pago
    pago_confirmado = models.BooleanField(
        default=False,
        help_text="¿El pago ha sido confirmado?"
    )
    fecha_confirmacion = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha de confirmación de la inscripción"
    )
    
    # Notas adicionales
    notas = models.TextField(
        blank=True,
        help_text="Notas o comentarios adicionales"
    )
    
    # Origen de la inscripción
    registro_masivo = models.BooleanField(
        default=False,
        help_text="¿Fue registrado mediante carga masiva?"
    )
    
    class Meta:
        verbose_name = 'Inscripción'
        verbose_name_plural = 'Inscripciones'
        ordering = ['-fecha_inscripcion']
        unique_together = ['evento', 'documento']
        indexes = [
            models.Index(fields=['evento', 'estado']),
            models.Index(fields=['codigo_qr']),
            models.Index(fields=['correo']),
        ]
    
    def __str__(self):
        return f"{self.get_nombre_completo()} - {self.evento.nombre}"
    
    def save(self, *args, **kwargs):
        """Override save para manejar lógica de negocio"""
        # Si el evento es gratuito, auto-confirmar
        if self.evento.es_gratuito and self.estado == 'PENDIENTE':
            self.estado = 'CONFIRMADA'
            self.pago_confirmado = True
            self.fecha_confirmacion = timezone.now()
        
        # Si hay un usuario asociado, completar datos faltantes (no sobrescribir si ya existen)
        if self.usuario:
            if not self.nombre and self.usuario.first_name:
                self.nombre = self.usuario.first_name
            if not self.apellido and self.usuario.last_name:
                self.apellido = self.usuario.last_name
            if not self.correo and self.usuario.email:
                self.correo = self.usuario.email
            if not self.telefono and self.usuario.telefono:
                self.telefono = self.usuario.telefono
            if not self.documento and self.usuario.documento:
                self.documento = self.usuario.documento
        
        super().save(*args, **kwargs)
    
    def get_nombre_completo(self):
        """Retorna el nombre completo del participante"""
        return f"{self.nombre} {self.apellido}"
    
    def confirmar(self):
        """Confirma la inscripción"""
        self.estado = 'CONFIRMADA'
        self.fecha_confirmacion = timezone.now()
        self.save()
    
    def cancelar(self):
        """Cancela la inscripción"""
        self.estado = 'CANCELADA'
        self.save()
    
    def rechazar(self):
        """Rechaza la inscripción"""
        self.estado = 'RECHAZADA'
        self.save()
    
    @property
    def porcentaje_asistencia(self):
        """
        Calcula el porcentaje de asistencia del participante (HU-18)
        """
        if self.evento.numero_sesiones == 0:
            return 0
        
        total_asistencias = self.asistencias.count()
        return (total_asistencias / self.evento.numero_sesiones) * 100
    
    @property
    def cumple_asistencia_minima(self):
        """Verifica si cumple el porcentaje mínimo de asistencia"""
        return self.porcentaje_asistencia >= self.evento.porcentaje_asistencia_minimo
    
    @property
    def puede_generar_certificado(self):
        """Verifica si puede generar certificado (HU-05, HU-19)"""
        return (
            self.evento.genera_certificado and
            self.estado == 'CONFIRMADA' and
            self.cumple_asistencia_minima
        )
    
    def generar_url_qr(self):
        """Genera la URL para el código QR"""
        from django.urls import reverse
        return reverse('asistencias:registrar_qr', kwargs={'codigo_qr': self.codigo_qr})


class RegistroMasivo(models.Model):
    """
    Modelo para registrar cargas masivas de inscripciones (HU-10)
    """
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name='registros_masivos'
    )
    archivo_original = models.FileField(
        upload_to='inscripciones/masivos/%Y/%m/',
        help_text="Archivo Excel/CSV original"
    )
    fecha_carga = models.DateTimeField(default=timezone.now)
    cargado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True
    )
    
    # Resultados de la carga
    total_registros = models.PositiveIntegerField(default=0)
    registros_exitosos = models.PositiveIntegerField(default=0)
    registros_fallidos = models.PositiveIntegerField(default=0)
    reporte_errores = models.TextField(
        blank=True,
        help_text="Detalle de errores encontrados"
    )
    
    class Meta:
        verbose_name = 'Registro Masivo'
        verbose_name_plural = 'Registros Masivos'
        ordering = ['-fecha_carga']
    
    def __str__(self):
        return f"Carga masiva {self.evento.nombre} - {self.fecha_carga.strftime('%d/%m/%Y')}"
