"""
Tests para modelos de Usuarios
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

Usuario = get_user_model()


@pytest.mark.django_db
class TestUsuarioModel:
    """Tests para el modelo Usuario"""
    
    def test_crear_usuario(self):
        """Test: Crear usuario básico (HU-11)"""
        usuario = Usuario.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='Test123456',
            first_name='Test',
            last_name='User',
            documento='12345678'
        )
        
        assert usuario.username == 'testuser'
        assert usuario.email == 'test@test.com'
        assert usuario.is_active
        assert usuario.activo
        assert usuario.rol == 'ASISTENTE'
    
    def test_usuario_puede_iniciar_sesion(self):
        """Test: Verificar si usuario puede iniciar sesión (HU-04)"""
        usuario = Usuario.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='Test123456',
            documento='12345678'
        )
        
        assert usuario.puede_iniciar_sesion()
        
        # Desactivar usuario
        usuario.activo = False
        usuario.save()
        assert not usuario.puede_iniciar_sesion()
    
    def test_bloqueo_por_intentos_fallidos(self):
        """Test: Bloqueo de cuenta tras intentos fallidos (HU-04)"""
        usuario = Usuario.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='Test123456',
            documento='12345678'
        )
        
        # Incrementar intentos fallidos
        for _ in range(4):
            usuario.incrementar_intentos_fallidos()
        
        assert usuario.intentos_fallidos == 4
        assert usuario.bloqueado_hasta is not None
        assert usuario.esta_bloqueado()
        assert not usuario.puede_iniciar_sesion()
    
    def test_roles_usuario(self):
        """Test: Verificar roles de usuario (HU-12)"""
        admin = Usuario.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='Test123456',
            documento='12345678',
            rol='ADMINISTRADOR'
        )
        
        organizador = Usuario.objects.create_user(
            username='org',
            email='org@test.com',
            password='Test123456',
            documento='87654321',
            rol='ORGANIZADOR'
        )
        
        asistente = Usuario.objects.create_user(
            username='asis',
            email='asis@test.com',
            password='Test123456',
            documento='11111111',
            rol='ASISTENTE'
        )
        
        assert admin.es_administrador()
        assert not admin.es_organizador()
        assert not admin.es_asistente()
        
        assert not organizador.es_administrador()
        assert organizador.es_organizador()
        assert not organizador.es_asistente()
        
        assert not asistente.es_administrador()
        assert not asistente.es_organizador()
        assert asistente.es_asistente()
        
        # Verificar permisos para gestionar eventos
        assert admin.puede_gestionar_eventos()
        assert organizador.puede_gestionar_eventos()
        assert not asistente.puede_gestionar_eventos()
    
    def test_desactivar_activar_usuario(self):
        """Test: Desactivar y activar usuario (HU-14)"""
        usuario = Usuario.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='Test123456',
            documento='12345678'
        )
        
        admin = Usuario.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='Test123456',
            documento='87654321',
            rol='ADMINISTRADOR'
        )
        
        # Desactivar usuario
        usuario.desactivar(usuario_modificador=admin)
        assert not usuario.activo
        assert usuario.fecha_desactivacion is not None
        
        # Activar usuario
        usuario.activar(usuario_modificador=admin)
        assert usuario.activo
        assert usuario.fecha_desactivacion is None
        assert usuario.intentos_fallidos == 0

