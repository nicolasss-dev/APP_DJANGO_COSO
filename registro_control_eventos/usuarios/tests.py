from django.test import TestCase
from django.utils import timezone
from .models import Usuario

class UsuarioRolesTestCase(TestCase):
	def setUp(self):
		self.admin = Usuario.objects.create_user(
			username='admin',
			password='adminpass',
			email='admin@example.com',
			documento='1001',
			rol='ADMINISTRADOR',
			is_superuser=True,
			is_staff=True
		)
		self.organizador = Usuario.objects.create_user(
			username='organizador',
			password='orgpass',
			email='org@example.com',
			documento='1002',
			rol='ORGANIZADOR'
		)
		self.asistente = Usuario.objects.create_user(
			username='asistente',
			password='asistpass',
			email='asist@example.com',
			documento='1003',
			rol='ASISTENTE'
		)

	def test_admin_role(self):
		self.assertTrue(self.admin.es_administrador())
		self.assertTrue(self.admin.is_superuser)
		self.assertTrue(self.admin.is_staff)
		self.assertEqual(self.admin.rol, 'ADMINISTRADOR')

	def test_organizador_role(self):
		self.assertTrue(self.organizador.es_organizador())
		self.assertEqual(self.organizador.rol, 'ORGANIZADOR')
		self.assertFalse(self.organizador.is_superuser)

	def test_asistente_role(self):
		self.assertTrue(self.asistente.es_asistente())
		self.assertEqual(self.asistente.rol, 'ASISTENTE')
		self.assertFalse(self.asistente.is_superuser)

	def test_gestionar_eventos(self):
		self.assertTrue(self.admin.puede_gestionar_eventos())
		self.assertTrue(self.organizador.puede_gestionar_eventos())
		self.assertFalse(self.asistente.puede_gestionar_eventos())

	def test_usuario_activo_y_desactivacion(self):
		self.assertTrue(self.admin.activo)
		self.admin.desactivar()
		self.assertFalse(self.admin.activo)
		self.assertIsNotNone(self.admin.fecha_desactivacion)

	def test_usuario_activar(self):
		self.organizador.desactivar()
		self.organizador.activar()
		self.assertTrue(self.organizador.activo)
		self.assertIsNone(self.organizador.fecha_desactivacion)
