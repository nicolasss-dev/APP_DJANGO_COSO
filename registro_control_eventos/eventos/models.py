"""
Modelos para la aplicación de Eventos
PRCE - Plataforma de Registro y Control de Eventos

HU-01: Creación de Eventos
HU-02: Edición de Eventos
HU-06: Eliminación de Eventos
HU-07: Clasificación por Tipo de Evento
HU-08: Subir Imagen Promocional
HU-09: Duplicar Evento Existente
"""

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from usuarios.models import Usuario


def validate_image_size(image):
    """
    Validador personalizado para tamaño de imagen (HU-08: máximo 2MB)
    """
    file_size = image.size
    limit_mb = 2
    if file_size > limit_mb * 1024 * 1024:
        raise ValidationError(f'La imagen es demasiado grande. Máximo {limit_mb} MB')


class TipoEvento(models.Model):
    """
    Catálogo de tipos de evento (HU-07)
    """
    TIPOS = [
        ('ACADEMICO', 'Académico'),
        ('CULTURAL', 'Cultural'),
        ('CORPORATIVO', 'Corporativo'),
        ('DEPORTIVO', 'Deportivo'),
        ('SOCIAL', 'Social'),
    ]
    
    nombre = models.CharField(
        max_length=20,
        choices=TIPOS,
        unique=True,
        help_text="Tipo de evento"
    )
    descripcion = models.TextField(
        blank=True,
        help_text="Descripción del tipo de evento"
    )
    color_badge = models.CharField(
        max_length=7,
        default='#6c757d',
        help_text="Color para el badge en hexadecimal (ej: #007bff)"
    )
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Tipo de Evento'
        verbose_name_plural = 'Tipos de Eventos'
        ordering = ['nombre']
    
    def __str__(self):
        return self.get_nombre_display()


class Evento(models.Model):
    """
    Modelo principal de Evento
    """
    ESTADO_CHOICES = [
        ('BORRADOR', 'Borrador'),
        ('PUBLICADO', 'Publicado'),
        ('EN_CURSO', 'En Curso'),
        ('FINALIZADO', 'Finalizado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    # Campos básicos (HU-01)
    nombre = models.CharField(
        max_length=200,
        help_text="Nombre del evento"
    )
    descripcion = models.TextField(
        help_text="Descripción detallada del evento"
    )
    tipo_evento = models.ForeignKey(
        TipoEvento,
        on_delete=models.PROTECT,
        related_name='eventos',
        help_text="Tipo de evento"
    )
    
    # Fechas y horarios
    fecha_inicio = models.DateTimeField(
        help_text="Fecha y hora de inicio del evento"
    )
    fecha_fin = models.DateTimeField(
        help_text="Fecha y hora de fin del evento"
    )
    
    # Ubicación
    lugar = models.CharField(
        max_length=200,
        help_text="Lugar donde se realizará el evento"
    )
    direccion = models.TextField(
        blank=True,
        help_text="Dirección completa del evento"
    )
    
    # Capacidad y costo
    cupo_maximo = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Número máximo de participantes"
    )
    costo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Costo de inscripción al evento"
    )
    
    # Imagen promocional (HU-08)
    imagen_banner = models.ImageField(
        upload_to='eventos/banners/%Y/%m/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png']),
            validate_image_size
        ],
        help_text="Banner promocional (JPG/PNG, máx 2MB, recomendado 1200x400px)"
    )
    
    # Estado y gestión
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='BORRADOR',
        help_text="Estado actual del evento"
    )
    
    # Auditoría
    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='eventos_creados',
        help_text="Usuario que creó el evento"
    )
    fecha_creacion = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha de creación del evento"
    )
    modificado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos_modificados',
        help_text="Último usuario que modificó el evento"
    )
    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        help_text="Fecha de última modificación"
    )
    
    # Campos adicionales
    requiere_aprobacion = models.BooleanField(
        default=False,
        help_text="¿Las inscripciones requieren aprobación?"
    )
    porcentaje_asistencia_minimo = models.PositiveIntegerField(
        default=80,
        validators=[MinValueValidator(0)],
        help_text="Porcentaje mínimo de asistencia para certificado"
    )
    genera_certificado = models.BooleanField(
        default=True,
        help_text="¿Este evento genera certificado?"
    )
    numero_sesiones = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Número de sesiones del evento"
    )
    
    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_inicio']),
            models.Index(fields=['tipo_evento']),
        ]
    
    def __str__(self):
        return f"{self.nombre} - {self.get_estado_display()}"
    
    def clean(self):
        """
        Validaciones personalizadas (HU-01)
        """
        super().clean()
        
        # Validar que fecha_fin sea posterior a fecha_inicio
        if self.fecha_fin and self.fecha_inicio:
            if self.fecha_fin <= self.fecha_inicio:
                raise ValidationError({
                    'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'
                })
    
    def save(self, *args, **kwargs):
        """Override save para ejecutar validaciones"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def cupos_disponibles(self):
        """Calcula los cupos disponibles del evento"""
        inscritos = self.inscripciones.filter(estado='CONFIRMADA').count()
        return max(0, self.cupo_maximo - inscritos)
    
    @property
    def esta_lleno(self):
        """Verifica si el evento está lleno (HU-03)"""
        return self.cupos_disponibles == 0
    
    @property
    def total_inscritos(self):
        """Total de inscritos confirmados"""
        return self.inscripciones.filter(estado='CONFIRMADA').count()
    
    @property
    def tiene_inscripciones_confirmadas(self):
        """Verifica si el evento tiene inscripciones confirmadas"""
        return self.inscripciones.filter(estado='CONFIRMADA').exists()
    
    @property
    def total_asistencias(self):
        """Total de asistencias registradas"""
        return self.inscripciones.filter(asistencias__isnull=False).distinct().count()
    
    @property
    def porcentaje_ocupacion(self):
        """Porcentaje de ocupación del evento"""
        if self.cupo_maximo == 0:
            return 0
        return (self.total_inscritos / self.cupo_maximo) * 100
    
    @property
    def es_gratuito(self):
        """Verifica si el evento es gratuito"""
        return self.costo == 0
    
    @property
    def esta_activo(self):
        """Verifica si el evento está activo"""
        return self.estado in ['PUBLICADO', 'EN_CURSO']
    
    @property
    def puede_inscribirse(self):
        """Verifica si se pueden realizar inscripciones"""
        return (
            self.estado == 'PUBLICADO' and
            not self.esta_lleno and
            self.fecha_inicio > timezone.now()
        )
    
    def duplicar(self, usuario):
        """
        Duplica el evento (HU-09)
        Retorna un nuevo evento con los mismos datos excepto fechas e inscripciones
        """
        from datetime import timedelta
        
        # Calcular fechas temporales (1 mes después de hoy, manteniendo la duración del evento original)
        fecha_inicio_temp = timezone.now() + timedelta(days=30)
        duracion = self.fecha_fin - self.fecha_inicio
        fecha_fin_temp = fecha_inicio_temp + duracion
        
        nuevo_evento = Evento(
            nombre=f"{self.nombre} (Copia)",
            descripcion=self.descripcion,
            tipo_evento=self.tipo_evento,
            fecha_inicio=fecha_inicio_temp,
            fecha_fin=fecha_fin_temp,
            lugar=self.lugar,
            direccion=self.direccion,
            cupo_maximo=self.cupo_maximo,
            costo=self.costo,
            estado='BORRADOR',
            creado_por=usuario,
            requiere_aprobacion=self.requiere_aprobacion,
            porcentaje_asistencia_minimo=self.porcentaje_asistencia_minimo,
            genera_certificado=self.genera_certificado,
            numero_sesiones=self.numero_sesiones,
        )
        # No copiar imagen_banner, inscripciones
        return nuevo_evento
    
    def cancelar(self, usuario):
        """Cancela el evento (HU-06, HU-23)"""
        self.estado = 'CANCELADO'
        self.modificado_por = usuario
        self.save()
    
    def publicar(self, usuario):
        """Publica el evento"""
        if self.estado == 'BORRADOR':
            self.estado = 'PUBLICADO'
            self.modificado_por = usuario
            self.save()
    
    def finalizar(self, usuario):
        """Finaliza el evento"""
        if self.estado in ['PUBLICADO', 'EN_CURSO']:
            self.estado = 'FINALIZADO'
            self.modificado_por = usuario
            self.save()
    
    def total_recaudado(self):
        """Calcula el total recaudado del evento"""
        from pagos.models import Pago
        return Pago.objects.filter(
            inscripcion__evento=self,
            estado='COMPLETADO'
        ).aggregate(
            total=models.Sum('monto')
        )['total'] or 0


class HistorialCambioEvento(models.Model):
    """
    Modelo para registrar cambios importantes en eventos (HU-02)
    """
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name='historial_cambios'
    )
    campo_modificado = models.CharField(max_length=50)
    valor_anterior = models.TextField()
    valor_nuevo = models.TextField()
    fecha_cambio = models.DateTimeField(default=timezone.now)
    modificado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True
    )
    
    class Meta:
        verbose_name = 'Historial de Cambio de Evento'
        verbose_name_plural = 'Historial de Cambios de Eventos'
        ordering = ['-fecha_cambio']
    
    def __str__(self):
        return f"{self.evento.nombre} - {self.campo_modificado} modificado"
