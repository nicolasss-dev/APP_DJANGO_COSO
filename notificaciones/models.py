"""
Modelos para la aplicación de Notificaciones
PRCE - Plataforma de Registro y Control de Eventos

HU-21: Confirmación de Inscripción
HU-22: Recordatorios Previos
HU-23: Notificación de Cambios o Cancelación
HU-24: Configuración de Plantillas de Correo
"""

from django.db import models
from django.utils import timezone
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import Template, Context
from django.conf import settings
from eventos.models import Evento
from inscripciones.models import Inscripcion
from usuarios.models import Usuario


class TipoNotificacion(models.Model):
    """
    Catálogo de tipos de notificación
    """
    TIPOS = [
        ('CONFIRMACION_INSCRIPCION', 'Confirmación de Inscripción'),
        ('RECORDATORIO_EVENTO', 'Recordatorio de Evento'),
        ('CAMBIO_EVENTO', 'Cambio en Evento'),
        ('CANCELACION_EVENTO', 'Cancelación de Evento'),
        ('CERTIFICADO_DISPONIBLE', 'Certificado Disponible'),
        ('PAGO_CONFIRMADO', 'Confirmación de Pago'),
        ('INSCRIPCION_APROBADA', 'Inscripción Aprobada'),
        ('INSCRIPCION_RECHAZADA', 'Inscripción Rechazada'),
    ]
    
    codigo = models.CharField(
        max_length=50,
        choices=TIPOS,
        unique=True,
        help_text="Código identificador del tipo"
    )
    nombre = models.CharField(
        max_length=100,
        help_text="Nombre descriptivo"
    )
    descripcion = models.TextField(
        blank=True,
        help_text="Descripción del tipo de notificación"
    )
    activo = models.BooleanField(
        default=True,
        help_text="¿Este tipo está activo?"
    )
    
    class Meta:
        verbose_name = 'Tipo de Notificación'
        verbose_name_plural = 'Tipos de Notificaciones'
        ordering = ['nombre']
    
    def __str__(self):
        return self.get_codigo_display()


class PlantillaCorreo(models.Model):
    """
    Plantillas personalizables para correos electrónicos (HU-24)
    """
    tipo_notificacion = models.ForeignKey(
        TipoNotificacion,
        on_delete=models.CASCADE,
        related_name='plantillas'
    )
    nombre = models.CharField(
        max_length=100,
        help_text="Nombre identificador de la plantilla"
    )
    asunto = models.CharField(
        max_length=200,
        help_text="Asunto del correo (acepta variables)"
    )
    cuerpo_texto = models.TextField(
        help_text="Cuerpo del correo en texto plano (acepta variables)"
    )
    cuerpo_html = models.TextField(
        blank=True,
        help_text="Cuerpo del correo en HTML (opcional, acepta variables)"
    )
    pie_pagina = models.TextField(
        blank=True,
        help_text="Pie de página del correo"
    )
    activa = models.BooleanField(
        default=False,
        help_text="¿Esta plantilla está activa?"
    )
    predeterminada = models.BooleanField(
        default=False,
        help_text="¿Es la plantilla predeterminada del sistema?"
    )
    fecha_creacion = models.DateTimeField(default=timezone.now)
    creada_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Variables disponibles documentadas
    variables_disponibles = models.TextField(
        default="{{nombre}}, {{evento}}, {{fecha}}, {{hora}}, {{lugar}}, {{codigo_qr}}",
        help_text="Variables disponibles para usar en la plantilla"
    )
    
    class Meta:
        verbose_name = 'Plantilla de Correo'
        verbose_name_plural = 'Plantillas de Correo'
        ordering = ['tipo_notificacion', '-activa', 'nombre']
        unique_together = ['tipo_notificacion', 'nombre']
    
    def __str__(self):
        return f"{self.tipo_notificacion.nombre} - {self.nombre}"
    
    def save(self, *args, **kwargs):
        """Si se activa, desactivar otras plantillas del mismo tipo"""
        if self.activa:
            PlantillaCorreo.objects.filter(
                tipo_notificacion=self.tipo_notificacion,
                activa=True
            ).exclude(pk=self.pk).update(activa=False)
        super().save(*args, **kwargs)
    
    def renderizar(self, contexto):
        """
        Renderiza la plantilla con el contexto proporcionado
        """
        asunto_template = Template(self.asunto)
        cuerpo_template = Template(self.cuerpo_texto)
        
        context = Context(contexto)
        
        asunto_renderizado = asunto_template.render(context)
        cuerpo_renderizado = cuerpo_template.render(context)
        
        if self.cuerpo_html:
            html_template = Template(self.cuerpo_html)
            html_renderizado = html_template.render(context)
        else:
            html_renderizado = None
        
        # Agregar pie de página
        if self.pie_pagina:
            cuerpo_renderizado += f"\n\n{self.pie_pagina}"
            if html_renderizado:
                html_renderizado += f"<br><br>{self.pie_pagina}"
        
        return {
            'asunto': asunto_renderizado,
            'cuerpo_texto': cuerpo_renderizado,
            'cuerpo_html': html_renderizado
        }


class Notificacion(models.Model):
    """
    Modelo para registrar notificaciones enviadas
    """
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('ENVIADO', 'Enviado'),
        ('ERROR', 'Error'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    tipo_notificacion = models.ForeignKey(
        TipoNotificacion,
        on_delete=models.PROTECT,
        related_name='notificaciones'
    )
    destinatario_email = models.EmailField(
        help_text="Correo del destinatario"
    )
    destinatario_nombre = models.CharField(
        max_length=200,
        blank=True,
        help_text="Nombre del destinatario"
    )
    asunto = models.CharField(
        max_length=200,
        help_text="Asunto del correo enviado"
    )
    cuerpo = models.TextField(
        help_text="Cuerpo del correo enviado"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE'
    )
    fecha_programada = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha programada para envío"
    )
    fecha_envio = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha real de envío"
    )
    intentos = models.PositiveIntegerField(
        default=0,
        help_text="Número de intentos de envío"
    )
    error_mensaje = models.TextField(
        blank=True,
        help_text="Mensaje de error si falló el envío"
    )
    
    # Relaciones opcionales
    evento = models.ForeignKey(
        Evento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notificaciones'
    )
    inscripcion = models.ForeignKey(
        Inscripcion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notificaciones'
    )
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha_programada']
        indexes = [
            models.Index(fields=['estado', 'fecha_programada']),
            models.Index(fields=['destinatario_email']),
        ]
    
    def __str__(self):
        return f"{self.tipo_notificacion} - {self.destinatario_email} - {self.get_estado_display()}"
    
    def enviar(self):
        """
        Envía la notificación por correo
        """
        try:
            email = EmailMultiAlternatives(
                subject=self.asunto,
                body=self.cuerpo,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[self.destinatario_email]
            )
            
            # Si hay contenido HTML, agregarlo
            if '<' in self.cuerpo and '>' in self.cuerpo:
                email.attach_alternative(self.cuerpo, "text/html")
            
            email.send()
            
            self.estado = 'ENVIADO'
            self.fecha_envio = timezone.now()
            self.intentos += 1
            self.error_mensaje = ''
            self.save()
            
            return True
            
        except Exception as e:
            self.estado = 'ERROR'
            self.intentos += 1
            self.error_mensaje = str(e)
            self.save()
            
            return False
    
    @classmethod
    def crear_desde_plantilla(cls, tipo_codigo, destinatario_email, contexto, evento=None, inscripcion=None):
        """
        Crea y envía una notificación usando una plantilla activa
        """
        try:
            tipo_notif = TipoNotificacion.objects.get(codigo=tipo_codigo, activo=True)
            plantilla = PlantillaCorreo.objects.filter(
                tipo_notificacion=tipo_notif,
                activa=True
            ).first()
            
            if not plantilla:
                raise ValueError(f"No hay plantilla activa para {tipo_codigo}")
            
            # Renderizar plantilla
            contenido = plantilla.renderizar(contexto)
            
            # Crear notificación
            notificacion = cls.objects.create(
                tipo_notificacion=tipo_notif,
                destinatario_email=destinatario_email,
                destinatario_nombre=contexto.get('nombre', ''),
                asunto=contenido['asunto'],
                cuerpo=contenido['cuerpo_html'] or contenido['cuerpo_texto'],
                evento=evento,
                inscripcion=inscripcion
            )
            
            # Enviar inmediatamente
            notificacion.enviar()
            
            return notificacion
            
        except Exception as e:
            # Registrar error en logs
            import logging
            logger = logging.getLogger('django')
            logger.error(f"Error al crear notificación: {str(e)}")
            return None


class ConfiguracionRecordatorio(models.Model):
    """
    Configuración de recordatorios automáticos (HU-22)
    """
    evento = models.OneToOneField(
        Evento,
        on_delete=models.CASCADE,
        related_name='configuracion_recordatorio'
    )
    activo = models.BooleanField(
        default=True,
        help_text="¿Los recordatorios están activos?"
    )
    horas_antes = models.PositiveIntegerField(
        default=24,
        help_text="Horas antes del evento para enviar recordatorio"
    )
    mensaje_personalizado = models.TextField(
        blank=True,
        help_text="Mensaje adicional para el recordatorio"
    )
    enviado = models.BooleanField(
        default=False,
        help_text="¿Ya se envió el recordatorio?"
    )
    fecha_envio = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha en que se envió el recordatorio"
    )
    
    class Meta:
        verbose_name = 'Configuración de Recordatorio'
        verbose_name_plural = 'Configuraciones de Recordatorios'
    
    def __str__(self):
        return f"Recordatorio: {self.evento.nombre} ({self.horas_antes}h antes)"
