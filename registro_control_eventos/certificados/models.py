"""
Modelos para la aplicación de Certificados
PRCE - Plataforma de Registro y Control de Eventos

HU-05 & HU-19: Generación Automática de Certificados
HU-20: Envío de Certificados por Correo
"""

from django.db import models
from django.utils import timezone
from inscripciones.models import Inscripcion
from usuarios.models import Usuario
import string
import random


def generar_codigo_verificacion():
    """
    Genera un código único alfanumérico de 10 caracteres (HU-05)
    """
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(random.choices(caracteres, k=10))


class Certificado(models.Model):
    """
    Modelo para certificados de participación
    """
    ESTADO_CHOICES = [
        ('GENERADO', 'Generado'),
        ('ENVIADO', 'Enviado'),
        ('ERROR', 'Error'),
    ]
    
    inscripcion = models.OneToOneField(
        Inscripcion,
        on_delete=models.CASCADE,
        related_name='certificado',
        help_text="Inscripción asociada al certificado"
    )
    codigo_verificacion = models.CharField(
        max_length=10,
        unique=True,
        default=generar_codigo_verificacion,
        help_text="Código único de verificación"
    )
    archivo_pdf = models.FileField(
        upload_to='certificados/%Y/%m/',
        blank=True,
        null=True,
        help_text="Archivo PDF del certificado"
    )
    fecha_generacion = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha de generación del certificado"
    )
    fecha_envio = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha de envío por correo"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='GENERADO',
        help_text="Estado del certificado"
    )
    intentos_envio = models.PositiveIntegerField(
        default=0,
        help_text="Número de intentos de envío"
    )
    error_envio = models.TextField(
        blank=True,
        help_text="Descripción del error en el envío"
    )
    
    class Meta:
        verbose_name = 'Certificado'
        verbose_name_plural = 'Certificados'
        ordering = ['-fecha_generacion']
        indexes = [
            models.Index(fields=['codigo_verificacion']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return f"Certificado {self.codigo_verificacion} - {self.inscripcion.get_nombre_completo()}"
    
    def generar_pdf(self):
        """
        Genera el PDF del certificado (HU-05, HU-19)
        """
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import cm
        from io import BytesIO
        from django.core.files.base import ContentFile
        import os
        
        # Crear buffer
        buffer = BytesIO()
        
        # Crear el canvas en orientación horizontal
        p = canvas.Canvas(buffer, pagesize=landscape(A4))
        width, height = landscape(A4)
        
        # Título del certificado
        p.setFont("Helvetica-Bold", 36)
        p.drawCentredString(width / 2, height - 5 * cm, "CERTIFICADO DE PARTICIPACIÓN")
        
        # Subtítulo
        p.setFont("Helvetica", 18)
        p.drawCentredString(width / 2, height - 7 * cm, "Se otorga a:")
        
        # Nombre del participante
        p.setFont("Helvetica-Bold", 28)
        p.drawCentredString(width / 2, height - 9 * cm, self.inscripcion.get_nombre_completo())
        
        # Descripción
        p.setFont("Helvetica", 16)
        texto = f"Por su participación en el evento"
        p.drawCentredString(width / 2, height - 11 * cm, texto)
        
        # Nombre del evento
        p.setFont("Helvetica-Bold", 20)
        p.drawCentredString(width / 2, height - 12.5 * cm, self.inscripcion.evento.nombre)
        
        # Fechas
        p.setFont("Helvetica", 14)
        fecha_inicio = self.inscripcion.evento.fecha_inicio.strftime('%d de %B de %Y')
        fecha_fin = self.inscripcion.evento.fecha_fin.strftime('%d de %B de %Y')
        p.drawCentredString(width / 2, height - 14 * cm, f"Realizado del {fecha_inicio} al {fecha_fin}")
        
        # Porcentaje de asistencia
        p.setFont("Helvetica", 12)
        p.drawCentredString(
            width / 2, height - 15.5 * cm,
            f"Con un porcentaje de asistencia del {self.inscripcion.porcentaje_asistencia:.1f}%"
        )
        
        # Código de verificación
        p.setFont("Helvetica", 10)
        p.drawCentredString(
            width / 2, 2 * cm,
            f"Código de verificación: {self.codigo_verificacion}"
        )
        
        # Fecha de emisión
        p.drawCentredString(
            width / 2, 1.5 * cm,
            f"Fecha de emisión: {self.fecha_generacion.strftime('%d de %B de %Y')}"
        )
        
        # Finalizar el PDF
        p.showPage()
        p.save()
        
        # Guardar el archivo
        buffer.seek(0)
        nombre_archivo = f"certificado_{self.codigo_verificacion}.pdf"
        self.archivo_pdf.save(nombre_archivo, ContentFile(buffer.read()), save=True)
        
        buffer.close()
        
        return self.archivo_pdf
    
    def enviar_por_correo(self):
        """
        Envía el certificado por correo electrónico (HU-20)
        """
        from django.core.mail import EmailMessage
        from django.conf import settings
        
        try:
            # Generar PDF si no existe
            if not self.archivo_pdf:
                self.generar_pdf()
            
            # Crear el correo
            asunto = f"Su certificado de participación - {self.inscripcion.evento.nombre}"
            
            mensaje = f"""
Estimado/a {self.inscripcion.get_nombre_completo()},

Nos complace informarle que su certificado de participación en el evento "{self.inscripcion.evento.nombre}" está listo.

Adjunto encontrará su certificado en formato PDF.

Código de verificación: {self.codigo_verificacion}
Porcentaje de asistencia: {self.inscripcion.porcentaje_asistencia:.1f}%

Puede verificar la autenticidad de este certificado en nuestra plataforma ingresando el código de verificación.

Saludos cordiales,
Equipo de Eventos
"""
            
            email = EmailMessage(
                subject=asunto,
                body=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[self.inscripcion.correo]
            )
            
            # Adjuntar el PDF
            email.attach_file(self.archivo_pdf.path)
            
            # Enviar
            email.send()
            
            # Actualizar estado
            self.estado = 'ENVIADO'
            self.fecha_envio = timezone.now()
            self.intentos_envio += 1
            self.error_envio = ''
            self.save()
            
            return True
            
        except Exception as e:
            # Registrar error
            self.estado = 'ERROR'
            self.intentos_envio += 1
            self.error_envio = str(e)
            self.save()
            
            return False
    
    @classmethod
    def generar_certificados_evento(cls, evento):
        """
        Genera certificados para todos los participantes elegibles de un evento (HU-05, HU-19)
        """
        # Obtener inscripciones que cumplen requisitos
        inscripciones_elegibles = evento.inscripciones.filter(
            estado='CONFIRMADA'
        )
        
        certificados_generados = []
        
        for inscripcion in inscripciones_elegibles:
            if inscripcion.puede_generar_certificado:
                # Verificar si ya tiene certificado
                certificado, created = cls.objects.get_or_create(
                    inscripcion=inscripcion
                )
                
                if created or not certificado.archivo_pdf:
                    certificado.generar_pdf()
                
                certificados_generados.append(certificado)
        
        return certificados_generados


class PlantillaCertificado(models.Model):
    """
    Modelo para plantillas personalizables de certificados
    """
    nombre = models.CharField(
        max_length=100,
        help_text="Nombre de la plantilla"
    )
    descripcion = models.TextField(
        blank=True,
        help_text="Descripción de la plantilla"
    )
    logo = models.ImageField(
        upload_to='certificados/logos/',
        blank=True,
        null=True,
        help_text="Logo institucional para el certificado"
    )
    activa = models.BooleanField(
        default=False,
        help_text="¿Esta plantilla está activa?"
    )
    fecha_creacion = models.DateTimeField(default=timezone.now)
    creada_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True
    )
    
    # Configuración de diseño
    color_primario = models.CharField(
        max_length=7,
        default='#2c3e50',
        help_text="Color primario en hexadecimal"
    )
    color_secundario = models.CharField(
        max_length=7,
        default='#34495e',
        help_text="Color secundario en hexadecimal"
    )
    
    class Meta:
        verbose_name = 'Plantilla de Certificado'
        verbose_name_plural = 'Plantillas de Certificados'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        """Si se activa esta plantilla, desactivar las demás"""
        if self.activa:
            PlantillaCertificado.objects.filter(activa=True).update(activa=False)
        super().save(*args, **kwargs)
