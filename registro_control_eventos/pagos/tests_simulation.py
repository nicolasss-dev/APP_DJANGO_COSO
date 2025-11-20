from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from eventos.models import Evento, TipoEvento
from inscripciones.models import Inscripcion
from usuarios.models import Usuario
from pagos.models import MetodoPago, Pago

class PaymentSimulationTest(TestCase):
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
        
        # Create payment methods
        MetodoPago.objects.create(nombre='Tarjeta', codigo='TARJETA', activo=True)
        MetodoPago.objects.create(nombre='Pasarela', codigo='PASARELA', activo=True)

    def test_payment_flow_integration(self):
        # 1. Register user (Simulate form submission)
        url_registro = reverse('inscripciones:registro_publico_evento', args=[self.evento.pk])
        self.client.login(username='user', password='password')
        
        # Initial GET to check form
        response = self.client.get(url_registro)
        self.assertEqual(response.status_code, 200)
        
        # POST to register
        data_registro = {
            'nombre': 'Test',
            'apellido': 'User',
            'documento': '1111111111',
            'correo': 'user@test.com',
            'telefono': '1234567890',
            'tipo_asistente': 'ESTUDIANTE'
        }
        response = self.client.post(url_registro, data_registro)
        
        # Should redirect to payment selection (NOT confirmation)
        inscripcion = Inscripcion.objects.get(correo='user@test.com')
        self.assertRedirects(response, reverse('pagos:seleccionar_metodo', args=[inscripcion.pk]))
        
        # 2. Check payment selection page
        url_seleccion = reverse('pagos:seleccionar_metodo', args=[inscripcion.pk])
        response = self.client.get(url_seleccion)
        self.assertContains(response, 'Tarjeta')
        
        # 4. Select Card Payment
        url_pago_tarjeta = reverse('pagos:pagar_tarjeta', args=[inscripcion.pk])
        response = self.client.get(url_pago_tarjeta)
        self.assertEqual(response.status_code, 200)
        
        # 5. Submit Card Payment
        data = {
            'numero_tarjeta': '4111111111111111',
            'nombre_titular': 'TEST USER',
            'fecha_expiracion': '12/30',
            'cvv': '123',
            'tipo_tarjeta': 'CREDITO',
            'cuotas': '1',
            'monto': '100.00'
        }
        response = self.client.post(url_pago_tarjeta, data)
        
        # Should redirect to inscription confirmation
        if response.status_code != 302:
            print("Form Errors:", response.context['form'].errors)
        self.assertRedirects(response, reverse('inscripciones:confirmacion_inscripcion', args=[inscripcion.pk]))
        
        # 6. Verify Payment Created and Registration Confirmed
        pago = Pago.objects.get(inscripcion=inscripcion)
        self.assertEqual(pago.estado, 'COMPLETADO')
        
        inscripcion.refresh_from_db()
        self.assertEqual(inscripcion.estado, 'CONFIRMADA')
        self.assertTrue(inscripcion.pago_confirmado)
