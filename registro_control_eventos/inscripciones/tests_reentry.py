from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from eventos.models import Evento, TipoEvento
from inscripciones.models import Inscripcion
from usuarios.models import Usuario

class RegistrationReentryTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.tipo_evento = TipoEvento.objects.create(
            nombre='PAID_TYPE',
            descripcion='Paid Type',
            color_badge='#000000'
        )
        
        self.admin = Usuario.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='password',
            rol='ADMINISTRADOR',
            documento='0000000000'
        )
        
        self.user = Usuario.objects.create_user(
            username='user',
            email='user@test.com',
            password='password',
            rol='ASISTENTE',
            documento='1111111111'
        )
        
        self.evento = Evento.objects.create(
            nombre='Paid Event',
            descripcion='Description',
            tipo_evento=self.tipo_evento,
            fecha_inicio=timezone.now() + timedelta(days=1),
            fecha_fin=timezone.now() + timedelta(days=1, hours=2),
            lugar='Test Place',
            cupo_maximo=10,
            costo=Decimal('100.00'),
            estado='PUBLICADO',
            creado_por=self.admin
        )

    def test_authenticated_user_reentry_redirects_to_payment(self):
        # 1. Create existing pending registration
        inscripcion = Inscripcion.objects.create(
            evento=self.evento,
            usuario=self.user,
            nombre='Test',
            apellido='User',
            documento='1111111111',
            correo='user@test.com',
            telefono='1234567890',
            estado='PENDIENTE'
        )
        
        self.client.login(username='user', password='password')
        
        # 2. Try to register again (POST)
        url_registro = reverse('inscripciones:registro_publico_evento', args=[self.evento.pk])
        response = self.client.post(url_registro, {})
        
        # 3. Should redirect to payment selection
        self.assertRedirects(response, reverse('pagos:seleccionar_metodo', args=[inscripcion.pk]))
        
    def test_anonymous_user_reentry_redirects_to_payment(self):
        # 1. Create existing pending registration (anonymous)
        inscripcion = Inscripcion.objects.create(
            evento=self.evento,
            nombre='Anon',
            apellido='User',
            documento='999999999',
            correo='anon@test.com',
            telefono='1234567890',
            estado='PENDIENTE'
        )
        
        # 2. Try to register again with SAME document
        url_registro = reverse('inscripciones:registro_publico_evento', args=[self.evento.pk])
        data = {
            'nombre': 'Anon',
            'apellido': 'User',
            'documento': '999999999',
            'correo': 'anon@test.com',
            'telefono': '1234567890',
            'tipo_asistente': 'ESTUDIANTE'
        }
        response = self.client.post(url_registro, data)
        
        # 3. Should redirect to payment selection
        self.assertRedirects(response, reverse('pagos:seleccionar_metodo', args=[inscripcion.pk]))
