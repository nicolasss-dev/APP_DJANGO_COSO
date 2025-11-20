"""
Script para inicializar datos básicos del sistema
"""

from django.core.management.base import BaseCommand
from eventos.models import TipoEvento
from notificaciones.models import TipoNotificacion
from pagos.models import MetodoPago


class Command(BaseCommand):
    help = 'Inicializa datos básicos del sistema (tipos de eventos, notificaciones, métodos de pago)'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando creación de datos básicos...\n')
        
        # Crear Tipos de Eventos
        self.stdout.write('Creando Tipos de Eventos...')
        tipos_eventos_creados = 0
        tipos_eventos = [
            ('ACADEMICO', 'Académico', 'Conferencias, talleres, seminarios, cursos', '#007bff'),
            ('CULTURAL', 'Cultural', 'Exposiciones, conciertos, festivales', '#6f42c1'),
            ('CORPORATIVO', 'Corporativo', 'Reuniones empresariales, capacitaciones', '#28a745'),
            ('DEPORTIVO', 'Deportivo', 'Competencias, torneos, carreras', '#fd7e14'),
            ('SOCIAL', 'Social', 'Celebraciones, reuniones comunitarias', '#20c997'),
        ]
        
        for codigo, nombre, descripcion, color in tipos_eventos:
            tipo, created = TipoEvento.objects.get_or_create(
                nombre=codigo,
                defaults={
                    'descripcion': descripcion,
                    'color_badge': color,
                    'activo': True
                }
            )
            if created:
                tipos_eventos_creados += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ {nombre}'))
            else:
                self.stdout.write(f'  - {nombre} ya existe')
        
        self.stdout.write(self.style.SUCCESS(f'\n{tipos_eventos_creados} tipos de eventos creados\n'))
        
        # Crear Tipos de Notificaciones
        self.stdout.write('Creando Tipos de Notificaciones...')
        tipos_notif_creados = 0
        tipos_notificaciones = [
            ('CONFIRMACION_INSCRIPCION', 'Confirmación de Inscripción', 'Notificación enviada al confirmar una inscripción'),
            ('RECORDATORIO_EVENTO', 'Recordatorio de Evento', 'Recordatorio previo al evento'),
            ('CAMBIO_EVENTO', 'Cambio en Evento', 'Notificación de cambios en un evento'),
            ('CANCELACION_EVENTO', 'Cancelación de Evento', 'Notificación de cancelación de evento'),
            ('CERTIFICADO_DISPONIBLE', 'Certificado Disponible', 'Notificación cuando el certificado está listo'),
            ('PAGO_CONFIRMADO', 'Confirmación de Pago', 'Confirmación de pago recibido'),
            ('INSCRIPCION_APROBADA', 'Inscripción Aprobada', 'Aprobación de inscripción'),
            ('INSCRIPCION_RECHAZADA', 'Inscripción Rechazada', 'Rechazo de inscripción'),
        ]
        
        for codigo, nombre, descripcion in tipos_notificaciones:
            tipo, created = TipoNotificacion.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'nombre': nombre,
                    'descripcion': descripcion,
                    'activo': True
                }
            )
            if created:
                tipos_notif_creados += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ {nombre}'))
            else:
                self.stdout.write(f'  - {nombre} ya existe')
        
        self.stdout.write(self.style.SUCCESS(f'\n{tipos_notif_creados} tipos de notificaciones creados\n'))
        
        # Crear Métodos de Pago
        self.stdout.write('Creando Métodos de Pago...')
        metodos_pago_creados = 0
        metodos_pago = [
            ('EFECTIVO', 'Efectivo', 'Pago en efectivo en oficinas', False),
            ('TRANSFERENCIA', 'Transferencia Bancaria', 'Transferencia o depósito bancario', True),
            ('TARJETA', 'Tarjeta de Crédito/Débito', 'Pago con tarjeta (simulado)', False),
            ('PASARELA', 'Pasarela de Pago Online', 'Pago a través de pasarela (simulado)', False),
        ]
        
        for codigo, nombre, descripcion, requiere_comprobante in metodos_pago:
            metodo, created = MetodoPago.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'nombre': nombre,
                    'descripcion': descripcion,
                    'requiere_comprobante': requiere_comprobante,
                    'activo': True
                }
            )
            if created:
                metodos_pago_creados += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ {nombre}'))
            else:
                self.stdout.write(f'  - {nombre} ya existe')
        
        self.stdout.write(self.style.SUCCESS(f'\n{metodos_pago_creados} métodos de pago creados\n'))
        
        # Resumen
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('RESUMEN'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(f'Tipos de Eventos: {TipoEvento.objects.count()} en total')
        self.stdout.write(f'Tipos de Notificaciones: {TipoNotificacion.objects.count()} en total')
        self.stdout.write(f'Métodos de Pago: {MetodoPago.objects.count()} en total')
        self.stdout.write(self.style.SUCCESS('\n✓ Inicialización completada exitosamente'))
