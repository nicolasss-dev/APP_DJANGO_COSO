from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from eventos.models import Evento, TipoEvento
from inscripciones.models import Inscripcion
from pagos.models import MetodoPago, Pago

User = get_user_model()

class PublicPaymentAccessTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Crear tipo de evento
        self.tipo_evento = TipoEvento.objects.create(
            nombre='ACADEMICO',
            descripcion='Evento académico'
        )
        

        # Crear usuario organizador
        self.organizador = User.objects.create_user(
            username='organizador',
            email='org@test.com',
            password='password123',
            rol='ORGANIZADOR',
            documento='1234567890'
        )
        
        # Crear usuario normal
        self.usuario = User.objects.create_user(
            username='usuario',
            email='user@test.com',
            password='password123',
            rol='ASISTENTE',
            activo=True
        )
        self.metodo_tarjeta = MetodoPago.objects.create(
            codigo='TARJETA',
            nombre='Tarjeta',
            activo=True
        )
        
        # Inscripción de usuario autenticado
        self.inscripcion_auth = Inscripcion.objects.create(
            evento=self.evento,
            usuario=self.usuario,
            estado='PENDIENTE'
        )
        
        # Inscripción anónima
        self.inscripcion_anon = Inscripcion.objects.create(
            evento=self.evento,
            nombre='Anonimo',
            apellido='Test',
            correo='anon@test.com',
            estado='PENDIENTE'
        )

    def test_anonymous_access_to_own_inscription(self):
        """Verificar que un usuario anónimo puede acceder a su inscripción"""
        url = reverse('pagos:seleccionar_metodo', args=[self.inscripcion_anon.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_anonymous_access_blocked_for_auth_inscription(self):
        """Verificar que un usuario anónimo NO puede acceder a una inscripción de usuario registrado"""
        url = reverse('pagos:seleccionar_metodo', args=[self.inscripcion_auth.id])
        response = self.client.get(url)
        # Debería redirigir al login
        self.assertRedirects(response, f"{reverse('usuarios:login')}?next={url}")

    def test_auth_user_access_to_own_inscription(self):
        """Verificar que un usuario autenticado puede acceder a su inscripción"""
        self.client.login(username='usuario', password='password123')
        url = reverse('pagos:seleccionar_metodo', args=[self.inscripcion_auth.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_auth_user_blocked_for_other_inscription(self):
        """Verificar que un usuario autenticado NO puede acceder a inscripción ajena"""
        # Crear otro usuario
        other_user = User.objects.create_user(
            username='other', 
            password='password123',
            documento='1122334455'
        )
        self.client.login(username='other', password='password123')
        
        url = reverse('pagos:seleccionar_metodo', args=[self.inscripcion_auth.id])
        response = self.client.get(url)
        # Debería redirigir a lista de inscripciones con mensaje de error
        self.assertRedirects(response, reverse('inscripciones:lista'))

    def test_organizer_access(self):
        """Verificar que un organizador puede acceder a cualquier inscripción"""
        self.client.login(username='organizador', password='password123')
        
        # Acceso a inscripción anónima
        url = reverse('pagos:seleccionar_metodo', args=[self.inscripcion_anon.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Acceso a inscripción de usuario
        url = reverse('pagos:seleccionar_metodo', args=[self.inscripcion_auth.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_payment_process_anonymous(self):
        """Verificar proceso de pago completo para usuario anónimo"""
        url = reverse('pagos:pagar_tarjeta', args=[self.inscripcion_anon.id])
        
        # GET del formulario
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # POST del pago
        data = {
            'nombre_titular': 'Anonimo Test',
            'numero_tarjeta': '4242424242424242',
            'fecha_expiracion': '12/30',
            'cvv': '123'
        }
        response = self.client.post(url, data)
        
        # Verificar redirección y estado
        self.assertRedirects(response, reverse('inscripciones:confirmacion_inscripcion', args=[self.inscripcion_anon.id]))
        
        self.inscripcion_anon.refresh_from_db()
        self.assertTrue(self.inscripcion_anon.pago_confirmado)
        self.assertEqual(self.inscripcion_anon.estado, 'CONFIRMADA')
