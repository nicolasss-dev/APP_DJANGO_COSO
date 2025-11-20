"""
Modelos para la aplicación de Pagos
PRCE - Plataforma de Registro y Control de Eventos

HU-25: Registro Manual de Pagos
HU-26: Integración con Pasarela de Pagos
HU-27: Reporte Financiero por Evento
"""

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from inscripciones.models import Inscripcion
from usuarios.models import Usuario
from eventos.models import Evento
from decimal import Decimal


class MetodoPago(models.Model):
    """
    Catálogo de métodos de pago
    """
    METODOS = [
        ('EFECTIVO', 'Efectivo'),
        ('TRANSFERENCIA', 'Transferencia Bancaria'),
        ('TARJETA', 'Tarjeta de Crédito/Débito'),
        ('PASARELA', 'Pasarela de Pagos'),
    ]
    
    codigo = models.CharField(
        max_length=20,
        choices=METODOS,
        unique=True,
        help_text="Código del método de pago"
    )
    nombre = models.CharField(
        max_length=100,
        help_text="Nombre del método de pago"
    )
    descripcion = models.TextField(
        blank=True,
        help_text="Descripción del método"
    )
    activo = models.BooleanField(
        default=True,
        help_text="¿Este método está activo?"
    )
    requiere_comprobante = models.BooleanField(
        default=False,
        help_text="¿Requiere adjuntar comprobante?"
    )
    
    class Meta:
        verbose_name = 'Método de Pago'
        verbose_name_plural = 'Métodos de Pago'
        ordering = ['nombre']
    
    def __str__(self):
        return self.get_codigo_display()


class Pago(models.Model):
    """
    Modelo para registrar pagos de inscripciones (HU-25)
    """
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('COMPLETADO', 'Completado'),
        ('RECHAZADO', 'Rechazado'),
        ('REEMBOLSADO', 'Reembolsado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    inscripcion = models.ForeignKey(
        Inscripcion,
        on_delete=models.CASCADE,
        related_name='pagos',
        help_text="Inscripción asociada al pago"
    )
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Monto del pago"
    )
    metodo_pago = models.ForeignKey(
        MetodoPago,
        on_delete=models.PROTECT,
        related_name='pagos',
        help_text="Método de pago utilizado"
    )
    referencia = models.CharField(
        max_length=100,
        blank=True,
        help_text="Número de referencia o transacción"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE',
        help_text="Estado del pago"
    )
    fecha_pago = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha del pago"
    )
    fecha_confirmacion = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha de confirmación del pago"
    )
    
    # Comprobante
    comprobante = models.FileField(
        upload_to='pagos/comprobantes/%Y/%m/',
        blank=True,
        null=True,
        help_text="Comprobante de pago (imagen o PDF)"
    )
    
    # Registro
    registrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pagos_registrados',
        help_text="Usuario que registró el pago (si es manual)"
    )
    
    # Datos de pasarela (HU-26)
    pasarela_transaccion_id = models.CharField(
        max_length=200,
        blank=True,
        help_text="ID de transacción de la pasarela"
    )
    pasarela_respuesta = models.TextField(
        blank=True,
        help_text="Respuesta completa de la pasarela (JSON)"
    )
    
    # Observaciones
    notas = models.TextField(
        blank=True,
        help_text="Notas adicionales sobre el pago"
    )
    
    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-fecha_pago']
        indexes = [
            models.Index(fields=['inscripcion', 'estado']),
            models.Index(fields=['referencia']),
            models.Index(fields=['pasarela_transaccion_id']),
        ]
    
    def __str__(self):
        return f"Pago {self.id} - {self.inscripcion.get_nombre_completo()} - ${self.monto}"
    
    def save(self, *args, **kwargs):
        """Override save para lógica de negocio"""
        is_new = self.pk is None
        
        super().save(*args, **kwargs)
        
        # Si el pago se completa, actualizar la inscripción
        if self.estado == 'COMPLETADO' and not self.inscripcion.pago_confirmado:
            self.inscripcion.pago_confirmado = True
            self.inscripcion.confirmar()
            
            # Generar código QR si no existe
            if not self.inscripcion.codigo_qr:
                import uuid
                self.inscripcion.codigo_qr = uuid.uuid4()
                self.inscripcion.save()
            
            # Enviar notificación de confirmación
            if is_new:
                self.enviar_notificacion_confirmacion()
    
    def confirmar(self, usuario=None):
        """Confirma el pago (HU-25)"""
        self.estado = 'COMPLETADO'
        self.fecha_confirmacion = timezone.now()
        if usuario:
            self.registrado_por = usuario
        self.save()
    
    def rechazar(self, motivo=''):
        """Rechaza el pago"""
        self.estado = 'RECHAZADO'
        if motivo:
            self.notas += f"\nMotivo de rechazo: {motivo}"
        self.save()
    
    def reembolsar(self, motivo=''):
        """Registra un reembolso"""
        self.estado = 'REEMBOLSADO'
        if motivo:
            self.notas += f"\nMotivo de reembolso: {motivo}"
        self.save()
    
    def enviar_notificacion_confirmacion(self):
        """Envía notificación de confirmación de pago"""
        from notificaciones.models import Notificacion
        
        contexto = {
            'nombre': self.inscripcion.get_nombre_completo(),
            'evento': self.inscripcion.evento.nombre,
            'monto': self.monto,
            'referencia': self.referencia or 'N/A',
            'fecha': self.fecha_pago.strftime('%d/%m/%Y'),
        }
        
        try:
            Notificacion.crear_desde_plantilla(
                tipo_codigo='PAGO_CONFIRMADO',
                destinatario_email=self.inscripcion.correo,
                contexto=contexto,
                evento=self.inscripcion.evento,
                inscripcion=self.inscripcion
            )
        except Exception as e:
            import logging
            logger = logging.getLogger('django')
            logger.error(f"Error al enviar notificación de pago: {str(e)}")
    
    @classmethod
    def obtener_reporte_evento(cls, evento):
        """
        Genera reporte financiero del evento (HU-27)
        """
        pagos_completados = cls.objects.filter(
            inscripcion__evento=evento,
            estado='COMPLETADO'
        )
        
        total_recaudado = pagos_completados.aggregate(
            total=models.Sum('monto')
        )['total'] or Decimal('0.00')
        
        pagos_pendientes = cls.objects.filter(
            inscripcion__evento=evento,
            estado='PENDIENTE'
        )
        
        total_pendiente = pagos_pendientes.aggregate(
            total=models.Sum('monto')
        )['total'] or Decimal('0.00')
        
        # Calcular total esperado
        inscritos_confirmados = evento.inscripciones.filter(estado='CONFIRMADA').count()
        total_esperado = evento.costo * inscritos_confirmados
        
        # Desglose por método de pago
        por_metodo = {}
        for metodo in MetodoPago.objects.filter(activo=True):
            total_metodo = pagos_completados.filter(
                metodo_pago=metodo
            ).aggregate(total=models.Sum('monto'))['total'] or Decimal('0.00')
            
            por_metodo[metodo.get_codigo_display()] = {
                'total': total_metodo,
                'cantidad': pagos_completados.filter(metodo_pago=metodo).count()
            }
        
        return {
            'total_recaudado': total_recaudado,
            'total_pendiente': total_pendiente,
            'total_esperado': total_esperado,
            'inscritos_confirmados': inscritos_confirmados,
            'costo_evento': evento.costo,
            'por_metodo': por_metodo,
            'pagos_completados': pagos_completados.count(),
            'pagos_pendientes': pagos_pendientes.count(),
        }


class ConfiguracionPasarela(models.Model):
    """
    Configuración para pasarelas de pago (HU-26)
    """
    PASARELAS = [
        ('PAYU', 'PayU'),
        ('WOMPI', 'Wompi'),
        ('STRIPE', 'Stripe'),
        ('MERCADOPAGO', 'Mercado Pago'),
    ]
    
    nombre = models.CharField(
        max_length=20,
        choices=PASARELAS,
        unique=True,
        help_text="Nombre de la pasarela"
    )
    activa = models.BooleanField(
        default=False,
        help_text="¿Esta pasarela está activa?"
    )
    api_key = models.CharField(
        max_length=200,
        blank=True,
        help_text="API Key / Secret Key"
    )
    public_key = models.CharField(
        max_length=200,
        blank=True,
        help_text="Public Key / Client ID"
    )
    url_api = models.URLField(
        blank=True,
        help_text="URL de la API de la pasarela"
    )
    modo_prueba = models.BooleanField(
        default=True,
        help_text="¿Está en modo de prueba?"
    )
    configuracion_adicional = models.JSONField(
        blank=True,
        null=True,
        help_text="Configuración adicional en formato JSON"
    )
    
    class Meta:
        verbose_name = 'Configuración de Pasarela'
        verbose_name_plural = 'Configuraciones de Pasarelas'
    
    def __str__(self):
        return f"{self.get_nombre_display()} - {'Activa' if self.activa else 'Inactiva'}"
