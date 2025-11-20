"""
Modelos para la aplicación de Asistencias
PRCE - Plataforma de Registro y Control de Eventos

HU-16: Registro de Asistencia Manual
HU-17: Escaneo de Código QR
HU-18: Cálculo de Porcentaje de Participación
"""

from django.db import models
from django.utils import timezone
from inscripciones.models import Inscripcion
from usuarios.models import Usuario


class Asistencia(models.Model):
    """
    Modelo para registrar asistencia de participantes
    """
    METODO_CHOICES = [
        ('MANUAL', 'Manual'),
        ('QR', 'Código QR'),
        ('AUTOMATICO', 'Automático'),
    ]
    
    inscripcion = models.ForeignKey(
        Inscripcion,
        on_delete=models.CASCADE,
        related_name='asistencias',
        help_text="Inscripción del participante"
    )
    sesion = models.PositiveIntegerField(
        default=1,
        help_text="Número de sesión del evento"
    )
    fecha_registro = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha y hora del registro de asistencia"
    )
    metodo_registro = models.CharField(
        max_length=20,
        choices=METODO_CHOICES,
        default='MANUAL',
        help_text="Método utilizado para registrar la asistencia"
    )
    registrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asistencias_registradas',
        help_text="Usuario que registró la asistencia (si es manual)"
    )
    
    # Datos de verificación para QR
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP desde donde se registró (para QR)"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="User agent del dispositivo (para QR)"
    )
    
    # Observaciones
    notas = models.TextField(
        blank=True,
        help_text="Notas adicionales sobre la asistencia"
    )
    
    class Meta:
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
        ordering = ['-fecha_registro']
        unique_together = ['inscripcion', 'sesion']
        indexes = [
            models.Index(fields=['inscripcion', 'sesion']),
            models.Index(fields=['fecha_registro']),
        ]
    
    def __str__(self):
        return f"{self.inscripcion.get_nombre_completo()} - Sesión {self.sesion}"
    
    def save(self, *args, **kwargs):
        """Override save para validaciones"""
        # Validar que la sesión no exceda el número de sesiones del evento
        if self.sesion > self.inscripcion.evento.numero_sesiones:
            raise ValueError(
                f"La sesión {self.sesion} excede el número de sesiones del evento "
                f"({self.inscripcion.evento.numero_sesiones})"
            )
        super().save(*args, **kwargs)
    
    @classmethod
    def registrar_manual(cls, inscripcion, sesion, usuario):
        """
        Registra asistencia de forma manual (HU-16)
        """
        # Verificar si ya existe asistencia para esta sesión
        if cls.objects.filter(inscripcion=inscripcion, sesion=sesion).exists():
            raise ValueError("Asistencia ya registrada para esta sesión")
        
        asistencia = cls.objects.create(
            inscripcion=inscripcion,
            sesion=sesion,
            metodo_registro='MANUAL',
            registrado_por=usuario
        )
        return asistencia
    
    @classmethod
    def registrar_qr(cls, codigo_qr, sesion, ip_address=None, user_agent=None):
        """
        Registra asistencia mediante código QR (HU-17)
        """
        try:
            inscripcion = Inscripcion.objects.get(codigo_qr=codigo_qr)
        except Inscripcion.DoesNotExist:
            raise ValueError("Código QR no válido")
        
        # Verificar si ya existe asistencia para esta sesión
        if cls.objects.filter(inscripcion=inscripcion, sesion=sesion).exists():
            raise ValueError("Asistencia ya registrada")
        
        asistencia = cls.objects.create(
            inscripcion=inscripcion,
            sesion=sesion,
            metodo_registro='QR',
            ip_address=ip_address,
            user_agent=user_agent
        )
        return asistencia
    
    @classmethod
    def obtener_estadisticas_evento(cls, evento):
        """
        Obtiene estadísticas de asistencia para un evento
        """
        total_inscritos = evento.inscripciones.filter(estado='CONFIRMADA').count()
        
        if total_inscritos == 0:
            return {
                'total_inscritos': 0,
                'total_con_asistencia': 0,
                'porcentaje_asistencia': 0,
                'por_sesion': []
            }
        
        inscripciones_con_asistencia = evento.inscripciones.filter(
            estado='CONFIRMADA',
            asistencias__isnull=False
        ).distinct().count()
        
        # Estadísticas por sesión
        estadisticas_sesiones = []
        for sesion in range(1, evento.numero_sesiones + 1):
            asistencias_sesion = cls.objects.filter(
                inscripcion__evento=evento,
                sesion=sesion
            ).count()
            estadisticas_sesiones.append({
                'sesion': sesion,
                'asistencias': asistencias_sesion,
                'porcentaje': (asistencias_sesion / total_inscritos * 100) if total_inscritos > 0 else 0
            })
        
        return {
            'total_inscritos': total_inscritos,
            'total_con_asistencia': inscripciones_con_asistencia,
            'porcentaje_asistencia': (inscripciones_con_asistencia / total_inscritos * 100),
            'por_sesion': estadisticas_sesiones
        }


class ControlAsistencia(models.Model):
    """
    Modelo para sesiones de control de asistencia
    """
    evento = models.ForeignKey(
        'eventos.Evento',
        on_delete=models.CASCADE,
        related_name='controles_asistencia'
    )
    sesion = models.PositiveIntegerField(
        help_text="Número de sesión"
    )
    fecha_sesion = models.DateTimeField(
        help_text="Fecha y hora de la sesión"
    )
    activo = models.BooleanField(
        default=True,
        help_text="¿El control de asistencia está activo?"
    )
    observaciones = models.TextField(
        blank=True,
        help_text="Observaciones sobre la sesión"
    )
    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True
    )
    fecha_creacion = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Control de Asistencia'
        verbose_name_plural = 'Controles de Asistencia'
        unique_together = ['evento', 'sesion']
        ordering = ['evento', 'sesion']
    
    def __str__(self):
        return f"{self.evento.nombre} - Sesión {self.sesion}"
    
    @property
    def total_asistentes(self):
        """Total de asistentes registrados en esta sesión"""
        return Asistencia.objects.filter(
            inscripcion__evento=self.evento,
            sesion=self.sesion
        ).count()
    
    @property
    def total_inscritos(self):
        """Total de inscritos al evento"""
        return self.evento.inscripciones.filter(estado='CONFIRMADA').count()
    
    @property
    def porcentaje_asistencia(self):
        """Porcentaje de asistencia de la sesión"""
        if self.total_inscritos == 0:
            return 0
        return (self.total_asistentes / self.total_inscritos) * 100
