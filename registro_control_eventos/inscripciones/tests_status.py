from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from eventos.models import Evento, TipoEvento
from inscripciones.models import Inscripcion
from usuarios.models import Usuario

class RegistrationStatusTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.tipo_evento = TipoEvento.objects.create(
            nombre='TEST_TYPE',
            descripcion='Test Type',
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
            nombre='Test Event',
            descripcion='Description',
            tipo_evento=self.tipo_evento,
            fecha_inicio=timezone.now() + timedelta(days=1),
            fecha_fin=timezone.now() + timedelta(days=1, hours=2),
            lugar='Test Place',
            cupo_maximo=10,
            costo=Decimal('0.00'),
            estado='PUBLICADO',
            creado_por=self.admin
        )

    def test_authenticated_user_already_registered_sees_message(self):
        # Register the user
        Inscripcion.objects.create(
            evento=self.evento,
            usuario=self.user,
            nombre=self.user.first_name or 'Test',
            apellido=self.user.last_name or 'User',
            documento=self.user.documento,
            correo=self.user.email,
            telefono=self.user.telefono or '1234567890',
            estado='CONFIRMADA'
        )
        
        # Login
        self.client.login(username='user', password='password')
        
        # Access registration page
        url = reverse('inscripciones:registro_publico_evento', args=[self.evento.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ya estás inscrito en este evento')
        self.assertNotContains(response, '<form method="post"')

    def test_authenticated_user_not_registered_sees_form(self):
        # Login
        self.client.login(username='user', password='password')
        
        # Access registration page
        url = reverse('inscripciones:registro_publico_evento', args=[self.evento.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Ya estás inscrito en este evento')
        self.assertContains(response, '<form method="post"')
