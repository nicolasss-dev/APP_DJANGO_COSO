"""
Tests para la aplicación de Inscripciones
Pruebas unitarias y de integración para el proceso de registro público
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from eventos.models import Evento, TipoEvento
from inscripciones.models import Inscripcion
from usuarios.models import Usuario


class RegistroPublicoViewTest(TestCase):
    """
    Tests para la vista de registro público (HU-03)
    Verifica que los eventos se carguen correctamente y se muestren adecuadamente
    """
    
    def setUp(self):
        """Configuración inicial de pruebas"""
        self.client = Client()
        
        # Crear tipo de evento
        self.tipo_evento = TipoEvento.objects.create(
            nombre='ACADEMICO',
            descripcion='Eventos académicos',
            color_badge='#3498db'
        )
        
        # Crear usuario administrador
        self.admin = Usuario.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpass123',
            rol='ADMINISTRADOR',
            documento='1234567890'
        )
        
        # Crear eventos de prueba
        self.evento_publicado = Evento.objects.create(
            nombre='Evento de Prueba Publicado',
            descripcion='Descripción del evento publicado',
            tipo_evento=self.tipo_evento,
            fecha_inicio=timezone.now() + timedelta(days=10),
            fecha_fin=timezone.now() + timedelta(days=10, hours=2),
            lugar='Auditorio Principal',
            cupo_maximo=100,
            costo=Decimal('0.00'),
            estado='PUBLICADO',
            creado_por=self.admin
        )
        
        self.evento_borrador = Evento.objects.create(
            nombre='Evento de Prueba Borrador',
            descripcion='Descripción del evento borrador',
            tipo_evento=self.tipo_evento,
            fecha_inicio=timezone.now() + timedelta(days=15),
            fecha_fin=timezone.now() + timedelta(days=15, hours=2),
            lugar='Sala B',
            cupo_maximo=50,
            costo=Decimal('10000.00'),
            estado='BORRADOR',
            creado_por=self.admin
        )
        
        self.evento_pasado = Evento.objects.create(
            nombre='Evento Pasado',
            descripcion='Evento que ya ocurrió',
            tipo_evento=self.tipo_evento,
            fecha_inicio=timezone.now() - timedelta(days=5),
            fecha_fin=timezone.now() - timedelta(days=5, hours=-2),
            lugar='Auditorio',
            cupo_maximo=30,
            costo=Decimal('0.00'),
            estado='PUBLICADO',
            creado_por=self.admin
        )
    
    def test_vista_registro_publico_accesible(self):
        """Test 1: Verificar que la vista es accesible sin login"""
        response = self.client.get(reverse('inscripciones:registro_publico'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inscripciones/registro_publico.html')
    
    def test_solo_muestra_eventos_publicados(self):
        """Test 2: Verificar que solo se muestran eventos PUBLICADOS"""
        response = self.client.get(reverse('inscripciones:registro_publico'))
        eventos = response.context['eventos']
        
        # Verificar que el evento publicado está en la lista
        self.assertIn(self.evento_publicado, eventos)
        
        # Verificar que el evento borrador NO está en la lista
        self.assertNotIn(self.evento_borrador, eventos)
    
    def test_no_muestra_eventos_pasados(self):
        """Test 3: Verificar que no se muestran eventos con fecha pasada"""
        response = self.client.get(reverse('inscripciones:registro_publico'))
        eventos = response.context['eventos']
        
        # Verificar que el evento pasado NO está en la lista
        self.assertNotIn(self.evento_pasado, eventos)
    
    def test_context_contiene_total_eventos(self):
        """Test 4: Verificar que el context incluye el total de eventos"""
        response = self.client.get(reverse('inscripciones:registro_publico'))
        
        self.assertIn('total_eventos', response.context)
        self.assertIn('eventos', response.context)
        
        # Debe haber 1 evento disponible (el publicado con fecha futura)
        self.assertEqual(response.context['total_eventos'], 1)
    
    def test_eventos_ordenados_por_fecha(self):
        """Test 5: Verificar que los eventos están ordenados por fecha de inicio"""
        # Crear otro evento publicado
        evento2 = Evento.objects.create(
            nombre='Evento Futuro 2',
            descripcion='Otro evento',
            tipo_evento=self.tipo_evento,
            fecha_inicio=timezone.now() + timedelta(days=5),
            fecha_fin=timezone.now() + timedelta(days=5, hours=2),
            lugar='Sala C',
            cupo_maximo=40,
            costo=Decimal('0.00'),
            estado='PUBLICADO',
            creado_por=self.admin
        )
        
        response = self.client.get(reverse('inscripciones:registro_publico'))
        eventos = response.context['eventos']
        
        # El primer evento debe ser el más próximo
        if len(eventos) > 1:
            self.assertLess(eventos[0].fecha_inicio, eventos[1].fecha_inicio)
    
    def test_no_muestra_eventos_llenos(self):
        """Test 6: Verificar que no se muestran eventos sin cupos disponibles"""
        # Crear evento con cupo 1
        evento_lleno = Evento.objects.create(
            nombre='Evento Lleno',
            descripcion='Evento sin cupos',
            tipo_evento=self.tipo_evento,
            fecha_inicio=timezone.now() + timedelta(days=20),
            fecha_fin=timezone.now() + timedelta(days=20, hours=2),
            lugar='Sala D',
            cupo_maximo=1,
            costo=Decimal('0.00'),
            estado='PUBLICADO',
            creado_por=self.admin
        )
        
        # Crear una inscripción para llenarlo
        Inscripcion.objects.create(
            evento=evento_lleno,
            nombre='Juan',
            apellido='Pérez',
            documento='9876543210',
            correo='juan@test.com',
            telefono='1234567890',
            estado='CONFIRMADA'
        )
        
        response = self.client.get(reverse('inscripciones:registro_publico'))
        eventos = response.context['eventos']
        
        # El evento lleno NO debe aparecer en la lista
        self.assertNotIn(evento_lleno, eventos)
    
    def test_template_maneja_sin_eventos(self):
        """Test 7: Verificar que el template maneja correctamente cuando no hay eventos"""
        # Eliminar todos los eventos
        Evento.objects.all().delete()
        
        response = self.client.get(reverse('inscripciones:registro_publico'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_eventos'], 0)
        self.assertContains(response, 'No hay eventos disponibles')


class RegistroPublicoEventoViewTest(TestCase):
    """
    Tests para la vista de registro a evento específico (HU-03)
    """
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        
        # Crear tipo de evento
        self.tipo_evento = TipoEvento.objects.create(
            nombre='CULTURAL',
            descripcion='Eventos culturales',
            color_badge='#9b59b6'
        )
        
        # Crear usuario
        self.admin = Usuario.objects.create_user(
            username='admin_test2',
            email='admin2@test.com',
            password='testpass123',
            rol='ADMINISTRADOR',
            documento='1234567891'
        )
        
        # Crear evento disponible
        self.evento = Evento.objects.create(
            nombre='Evento para Inscripción',
            descripcion='Descripción del evento',
            tipo_evento=self.tipo_evento,
            fecha_inicio=timezone.now() + timedelta(days=7),
            fecha_fin=timezone.now() + timedelta(days=7, hours=3),
            lugar='Teatro Municipal',
            cupo_maximo=50,
            costo=Decimal('5000.00'),
            estado='PUBLICADO',
            creado_por=self.admin
        )
    
    def test_vista_registro_evento_accesible(self):
        """Test 8: Verificar que la vista es accesible"""
        url = reverse('inscripciones:registro_publico_evento', args=[self.evento.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inscripciones/registro_publico_evento.html')
    
    def test_context_contiene_evento(self):
        """Test 9: Verificar que el context incluye el evento"""
        url = reverse('inscripciones:registro_publico_evento', args=[self.evento.pk])
        response = self.client.get(url)
        
        self.assertIn('evento', response.context)
        self.assertEqual(response.context['evento'], self.evento)
    
    def test_evento_inexistente_retorna_404(self):
        """Test 10: Verificar que evento inexistente retorna 404"""
        url = reverse('inscripciones:registro_publico_evento', args=[9999])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)
    
    def test_evento_no_disponible_redirige(self):
        """Test 11: Verificar que evento no disponible redirige con mensaje"""
        # Cambiar estado del evento
        self.evento.estado = 'CANCELADO'
        self.evento.save()
        
        url = reverse('inscripciones:registro_publico_evento', args=[self.evento.pk])
        response = self.client.get(url)
        
        # Debe redirigir
        self.assertEqual(response.status_code, 302)
    
    def test_post_muestra_mensaje_desarrollo(self):
        """Test 12: Verificar que POST muestra mensaje de desarrollo"""
        url = reverse('inscripciones:registro_publico_evento', args=[self.evento.pk])
        
        data = {
            'nombre': 'María',
            'apellido': 'García',
            'documento': '1122334455',
            'correo': 'maria@test.com',
            'telefono': '3001234567'
        }
        
        response = self.client.post(url, data)
        
        # Debe redirigir
        self.assertEqual(response.status_code, 302)


class InscripcionModelTest(TestCase):
    """
    Tests para el modelo de Inscripción
    """
    
    def setUp(self):
        """Configuración inicial"""
        # Crear tipo de evento
        self.tipo_evento = TipoEvento.objects.create(
            nombre='DEPORTIVO',
            descripcion='Eventos deportivos',
            color_badge='#e74c3c'
        )
        
        # Crear usuario
        self.admin = Usuario.objects.create_user(
            username='admin_test3',
            email='admin3@test.com',
            password='testpass123',
            rol='ADMINISTRADOR',
            documento='1234567892'
        )
        
        # Crear evento
        self.evento = Evento.objects.create(
            nombre='Maratón de Programación',
            descripcion='Evento de programación',
            tipo_evento=self.tipo_evento,
            fecha_inicio=timezone.now() + timedelta(days=30),
            fecha_fin=timezone.now() + timedelta(days=30, hours=8),
            lugar='Campus Universitario',
            cupo_maximo=100,
            costo=Decimal('0.00'),
            estado='PUBLICADO',
            creado_por=self.admin,
            numero_sesiones=3
        )
    
    def test_inscripcion_evento_gratuito_auto_confirma(self):
        """Test 13: Verificar que inscripción a evento gratuito se auto-confirma"""
        inscripcion = Inscripcion.objects.create(
            evento=self.evento,
            nombre='Carlos',
            apellido='Rodríguez',
            documento='5566778899',
            correo='carlos@test.com',
            telefono='3109876543'
        )
        
        # Debe estar confirmada automáticamente
        self.assertEqual(inscripcion.estado, 'CONFIRMADA')
        self.assertTrue(inscripcion.pago_confirmado)
    
    def test_nombre_completo(self):
        """Test 14: Verificar método get_nombre_completo"""
        inscripcion = Inscripcion.objects.create(
            evento=self.evento,
            nombre='Ana',
            apellido='Martínez',
            documento='7788990011',
            correo='ana@test.com',
            telefono='3207654321'
        )
        
        self.assertEqual(inscripcion.get_nombre_completo(), 'Ana Martínez')
    
    def test_porcentaje_asistencia_inicial(self):
        """Test 15: Verificar que porcentaje de asistencia inicial es 0"""
        inscripcion = Inscripcion.objects.create(
            evento=self.evento,
            nombre='Luis',
            apellido='Fernández',
            documento='9988776655',
            correo='luis@test.com',
            telefono='3151234567'
        )
        
        self.assertEqual(inscripcion.porcentaje_asistencia, 0)


class IntegrationTest(TestCase):
    """
    Tests de integración para el flujo completo de registro
    """
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        
        # Crear tipo de evento
        self.tipo_evento = TipoEvento.objects.create(
            nombre='SOCIAL',
            descripcion='Eventos sociales',
            color_badge='#1abc9c'
        )
        
        # Crear usuario
        self.admin = Usuario.objects.create_user(
            username='admin_test4',
            email='admin4@test.com',
            password='testpass123',
            rol='ADMINISTRADOR',
            documento='1234567893'
        )
        
        # Crear evento
        self.evento = Evento.objects.create(
            nombre='Fiesta de Integración',
            descripcion='Evento de integración',
            tipo_evento=self.tipo_evento,
            fecha_inicio=timezone.now() + timedelta(days=14),
            fecha_fin=timezone.now() + timedelta(days=14, hours=4),
            lugar='Salón de Eventos',
            cupo_maximo=200,
            costo=Decimal('0.00'),
            estado='PUBLICADO',
            creado_por=self.admin
        )
    
    def test_flujo_completo_registro(self):
        """Test 16: Probar el flujo completo de registro de visitante"""
        # Paso 1: Acceder a la página de eventos públicos
        response1 = self.client.get(reverse('inscripciones:registro_publico'))
        self.assertEqual(response1.status_code, 200)
        self.assertIn(self.evento, response1.context['eventos'])
        
        # Paso 2: Acceder al formulario de inscripción
        url_inscripcion = reverse('inscripciones:registro_publico_evento', args=[self.evento.pk])
        response2 = self.client.get(url_inscripcion)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.context['evento'], self.evento)
        
        # Paso 3: Enviar formulario de inscripción (placeholder por ahora)
        data = {
            'nombre': 'Pedro',
            'apellido': 'Sánchez',
            'documento': '4455667788',
            'correo': 'pedro@test.com',
            'telefono': '3167890123'
        }
        response3 = self.client.post(url_inscripcion, data)
        
        # Debe redirigir (aunque la funcionalidad esté en desarrollo)
        self.assertEqual(response3.status_code, 302)


def run_tests():
    """
    Función para ejecutar todos los tests desde Django shell
    """
    from django.core.management import call_command
    call_command('test', 'inscripciones', verbosity=2)


class FormularioInscripcionTest(TestCase):
    """
    Tests para el formulario de inscripción pública
    """
    
    def setUp(self):
        """Configuración inicial"""
        # Crear tipo de evento
        self.tipo_evento = TipoEvento.objects.create(
            nombre='CORPORATIVO',
            descripcion='Eventos corporativos',
            color_badge='#34495e'
        )
        
        # Crear usuario
        self.admin = Usuario.objects.create_user(
            username='admin_test5',
            email='admin5@test.com',
            password='testpass123',
            rol='ADMINISTRADOR',
            documento='1234567894'
        )
        
        # Crear evento
        self.evento = Evento.objects.create(
            nombre='Taller Corporativo',
            descripcion='Taller de capacitación',
            tipo_evento=self.tipo_evento,
            fecha_inicio=timezone.now() + timedelta(days=10),
            fecha_fin=timezone.now() + timedelta(days=10, hours=4),
            lugar='Centro de Convenciones',
            cupo_maximo=30,
            costo=Decimal('0.00'),
            estado='PUBLICADO',
            creado_por=self.admin
        )
    
    def test_formulario_valido(self):
        """Test 17: Verificar que el formulario acepta datos válidos"""
        from inscripciones.forms import InscripcionPublicaForm
        
        data = {
            'nombre': 'Roberto',
            'apellido': 'Torres',
            'documento': '1234567890',
            'correo': 'roberto@test.com',
            'telefono': '3001234567'
        }
        
        form = InscripcionPublicaForm(data=data, evento=self.evento)
        self.assertTrue(form.is_valid())
    
    def test_formulario_email_invalido(self):
        """Test 18: Verificar validación de email inválido"""
        from inscripciones.forms import InscripcionPublicaForm
        
        data = {
            'nombre': 'Roberto',
            'apellido': 'Torres',
            'documento': '1234567890',
            'correo': 'email-invalido',
            'telefono': '3001234567'
        }
        
        form = InscripcionPublicaForm(data=data, evento=self.evento)
        self.assertFalse(form.is_valid())
        self.assertIn('correo', form.errors)
    
    def test_formulario_documento_invalido(self):
        """Test 19: Verificar validación de documento inválido"""
        from inscripciones.forms import InscripcionPublicaForm
        
        data = {
            'nombre': 'Roberto',
            'apellido': 'Torres',
            'documento': 'ABC123',  # Debe ser solo números
            'correo': 'roberto@test.com',
            'telefono': '3001234567'
        }
        
        form = InscripcionPublicaForm(data=data, evento=self.evento)
        self.assertFalse(form.is_valid())
        self.assertIn('documento', form.errors)
    
    def test_formulario_inscripcion_duplicada(self):
        """Test 20: Verificar que no permite inscripciones duplicadas"""
        from inscripciones.forms import InscripcionPublicaForm
        
        # Crear inscripción existente
        Inscripcion.objects.create(
            evento=self.evento,
            nombre='Roberto',
            apellido='Torres',
            documento='1234567890',
            correo='roberto@test.com',
            telefono='3001234567',
            estado='CONFIRMADA'
        )
        
        # Intentar crear otra con el mismo correo
        data = {
            'nombre': 'Roberto',
            'apellido': 'Torres',
            'documento': '9876543210',
            'correo': 'roberto@test.com',
            'telefono': '3001234567'
        }
        
        form = InscripcionPublicaForm(data=data, evento=self.evento)
        self.assertFalse(form.is_valid())
        self.assertIn('correo', form.errors)


class GuardadoInscripcionTest(TestCase):
    """
    Tests para el guardado completo de inscripciones
    """
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        
        # Crear tipo de evento
        self.tipo_evento = TipoEvento.objects.create(
            nombre='SOCIAL',
            descripcion='Eventos sociales',
            color_badge='#1abc9c'
        )
        
        # Crear usuario
        self.admin = Usuario.objects.create_user(
            username='admin_test6',
            email='admin6@test.com',
            password='testpass123',
            rol='ADMINISTRADOR',
            documento='1234567895'
        )
        
        # Crear evento gratuito
        self.evento_gratuito = Evento.objects.create(
            nombre='Evento Gratuito Test',
            descripcion='Evento de prueba gratuito',
            tipo_evento=self.tipo_evento,
            fecha_inicio=timezone.now() + timedelta(days=20),
            fecha_fin=timezone.now() + timedelta(days=20, hours=5),
            lugar='Plaza Central',
            cupo_maximo=100,
            costo=Decimal('0.00'),
            estado='PUBLICADO',
            creado_por=self.admin
        )
        
        # Crear evento con costo
        self.evento_pago = Evento.objects.create(
            nombre='Evento con Costo Test',
            descripcion='Evento de prueba con costo',
            tipo_evento=self.tipo_evento,
            fecha_inicio=timezone.now() + timedelta(days=25),
            fecha_fin=timezone.now() + timedelta(days=25, hours=3),
            lugar='Teatro',
            cupo_maximo=50,
            costo=Decimal('15000.00'),
            estado='PUBLICADO',
            creado_por=self.admin
        )
    
    def test_inscripcion_evento_gratuito_guarda_correctamente(self):
        """Test 21: Verificar que se guarda correctamente inscripción a evento gratuito"""
        url = reverse('inscripciones:registro_publico_evento', args=[self.evento_gratuito.pk])
        
        data = {
            'nombre': 'Camila',
            'apellido': 'Jiménez',
            'documento': '5544332211',
            'correo': 'camila@test.com',
            'telefono': '3208765432'
        }
        
        response = self.client.post(url, data)
        
        # Debe redirigir a confirmación
        self.assertEqual(response.status_code, 302)
        
        # Verificar que se creó la inscripción
        self.assertTrue(Inscripcion.objects.filter(correo='camila@test.com').exists())
        
        # Verificar que está confirmada automáticamente
        inscripcion = Inscripcion.objects.get(correo='camila@test.com')
        self.assertEqual(inscripcion.estado, 'CONFIRMADA')
        self.assertTrue(inscripcion.pago_confirmado)
    
    def test_inscripcion_evento_pago_queda_pendiente(self):
        """Test 22: Verificar que inscripción a evento con costo queda PENDIENTE"""
        url = reverse('inscripciones:registro_publico_evento', args=[self.evento_pago.pk])
        
        data = {
            'nombre': 'Diego',
            'apellido': 'Ramírez',
            'documento': '6677889900',
            'correo': 'diego@test.com',
            'telefono': '3159876543'
        }
        
        response = self.client.post(url, data)
        
        # Debe redirigir
        self.assertEqual(response.status_code, 302)
        
        # Verificar que se creó la inscripción
        inscripcion = Inscripcion.objects.get(correo='diego@test.com')
        
        # Debe estar PENDIENTE hasta que pague
        self.assertEqual(inscripcion.estado, 'PENDIENTE')
        self.assertFalse(inscripcion.pago_confirmado)
    
    def test_no_permite_inscripcion_duplicada_mismo_correo(self):
        """Test 23: Verificar que no permite inscripción duplicada con mismo correo"""
        url = reverse('inscripciones:registro_publico_evento', args=[self.evento_gratuito.pk])
        
        # Primera inscripción
        data = {
            'nombre': 'Laura',
            'apellido': 'Morales',
            'documento': '7788990011',
            'correo': 'laura@test.com',
            'telefono': '3107654321'
        }
        
        # Primera inscripción exitosa
        self.client.post(url, data)
        
        # Intentar segunda inscripción con el mismo correo
        data2 = {
            'nombre': 'Laura',
            'apellido': 'Morales',
            'documento': '7788990011',
            'correo': 'laura@test.com',
            'telefono': '3107654321'
        }
        
        response = self.client.post(url, data2)
        
        # No debe crear segunda inscripción
        self.assertEqual(Inscripcion.objects.filter(correo='laura@test.com').count(), 1)


# Resumen de pruebas implementadas:
# ✅ Test 1-7: Vista registro_publico (carga de eventos, filtros, ordenamiento)
# ✅ Test 8-12: Vista registro_publico_evento (acceso, validaciones)
# ✅ Test 13-15: Modelo Inscripcion (auto-confirmación, métodos)
# ✅ Test 16: Integración completa del flujo de registro
# ✅ Test 17-20: Formulario de inscripción (validaciones)
# ✅ Test 21-23: Guardado de inscripciones (gratuito, pago, duplicadas)
