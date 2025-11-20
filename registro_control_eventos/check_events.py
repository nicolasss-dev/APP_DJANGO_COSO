import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'registro_control_eventos.settings')
django.setup()

from eventos.models import Evento
from django.utils import timezone

print('=== DIAGNÓSTICO DE EVENTOS ===')
print(f'Total eventos en BD: {Evento.objects.count()}')

eventos_todos = Evento.objects.all()
for e in eventos_todos:
    print(f'\n  Evento: {e.nombre}')
    print(f'  Estado: {e.estado}')
    print(f'  Fecha inicio: {e.fecha_inicio}')
    print(f'  Fecha actual: {timezone.now()}')
    print(f'  Es futuro: {e.fecha_inicio >= timezone.now()}')

print(f'\n\nEventos PUBLICADOS: {Evento.objects.filter(estado="PUBLICADO").count()}')
eventos_pub_futuros = Evento.objects.filter(estado='PUBLICADO', fecha_inicio__gte=timezone.now())
print(f'Eventos PUBLICADOS con fecha futura: {eventos_pub_futuros.count()}')

for e in eventos_pub_futuros:
    print(f'  - {e.nombre}')
