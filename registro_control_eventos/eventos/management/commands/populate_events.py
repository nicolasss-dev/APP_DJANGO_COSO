from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from eventos.models import Evento, TipoEvento
from usuarios.models import Usuario

class Command(BaseCommand):
    help = 'Populate database with test events'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating test data...')
        
        # Ensure admin user exists
        admin_user, created = Usuario.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'rol': 'ADMINISTRADOR',
                'documento': '0000000000'
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('Created admin user')

        # Create Event Types
        tipos = [
            ('Conferencia', '#4e73df', 'fa-microphone'),
            ('Taller', '#1cc88a', 'fa-tools'),
            ('Seminario', '#36b9cc', 'fa-users'),
            ('Networking', '#f6c23e', 'fa-handshake'),
        ]
        
        tipo_objs = {}
        for nombre, color, icono in tipos:
            tipo, _ = TipoEvento.objects.get_or_create(
                nombre=nombre,
                defaults={'color_badge': color, 'descripcion': f'Eventos tipo {nombre}'}
            )
            tipo_objs[nombre] = tipo
            
        # Create Events
        now = timezone.now()
        
        events_data = [
            {
                'nombre': 'Conferencia Tech 2025',
                'tipo': 'Conferencia',
                'inicio': now + timedelta(days=5),
                'fin': now + timedelta(days=5, hours=8),
                'costo': Decimal('0.00'),
                'cupo': 100,
                'estado': 'PUBLICADO',
                'lugar': 'Auditorio Principal'
            },
            {
                'nombre': 'Taller de Python Avanzado',
                'tipo': 'Taller',
                'inicio': now + timedelta(days=10),
                'fin': now + timedelta(days=10, hours=4),
                'costo': Decimal('50.00'),
                'cupo': 20,
                'estado': 'PUBLICADO',
                'lugar': 'Sala de Cómputo 1'
            },
            {
                'nombre': 'Seminario de IA Generativa',
                'tipo': 'Seminario',
                'inicio': now + timedelta(days=15),
                'fin': now + timedelta(days=15, hours=6),
                'costo': Decimal('120.00'),
                'cupo': 50,
                'estado': 'PUBLICADO',
                'lugar': 'Centro de Convenciones'
            },
            {
                'nombre': 'Networking Empresarial',
                'tipo': 'Networking',
                'inicio': now + timedelta(days=2),
                'fin': now + timedelta(days=2, hours=3),
                'costo': Decimal('0.00'),
                'cupo': 30,
                'estado': 'BORRADOR',
                'lugar': 'Terraza Hotel Central'
            },
            {
                'nombre': 'Evento Pasado 2024',
                'tipo': 'Conferencia',
                'inicio': now - timedelta(days=30),
                'fin': now - timedelta(days=30, hours=5),
                'costo': Decimal('0.00'),
                'cupo': 100,
                'estado': 'PUBLICADO',
                'lugar': 'Virtual'
            }
        ]
        
        for data in events_data:
            # Ensure end time is strictly after start time
            if data['fin'] <= data['inicio']:
                data['fin'] = data['inicio'] + timedelta(hours=1)

            Evento.objects.update_or_create(
                nombre=data['nombre'],
                defaults={
                    'tipo_evento': tipo_objs[data['tipo']],
                    'fecha_inicio': data['inicio'],
                    'fecha_fin': data['fin'],
                    'costo': data['costo'],
                    'cupo_maximo': data['cupo'],
                    'estado': data['estado'],
                    'lugar': data['lugar'],
                    'descripcion': f"Descripción detallada para {data['nombre']}",
                    'creado_por': admin_user
                }
            )
            
        self.stdout.write(self.style.SUCCESS('Successfully populated database with test events'))
