"""
Tests para modelos de Eventos
"""

import pytest
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError

from eventos.models import Evento, TipoEvento
from usuarios.models import Usuario


@pytest.mark.django_db
class TestEventoModel:
    """Tests para el modelo Evento"""
    
    @pytest.fixture
    def usuario_organizador(self):
        """Fixture: Crear usuario organizador"""
        return Usuario.objects.create_user(
            username='organizador',
            email='org@test.com',
            password='Test123456',
            documento='12345678',
            rol='ORGANIZADOR'
        )
    
    @pytest.fixture
    def tipo_evento(self):
        """Fixture: Crear tipo de evento"""
        return TipoEvento.objects.create(
            nombre='ACADEMICO',
            descripcion='Evento académico',
            color_badge='#007bff'
        )
    
    def test_crear_evento(self, usuario_organizador, tipo_evento):
        """Test: Crear evento básico (HU-01)"""
        fecha_inicio = timezone.now() + timedelta(days=7)
        fecha_fin = fecha_inicio + timedelta(hours=3)
        
        evento = Evento.objects.create(
            nombre='Evento de Prueba',
            descripcion='Descripción del evento',
            tipo_evento=tipo_evento,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            lugar='Auditorio Principal',
            cupo_maximo=100,
            costo=0,
            creado_por=usuario_organizador
        )
        
        assert evento.nombre == 'Evento de Prueba'
        assert evento.estado == 'BORRADOR'
        assert evento.es_gratuito
        assert evento.cupo_maximo == 100
    
    def test_validacion_fechas(self, usuario_organizador, tipo_evento):
        """Test: Validar que fecha fin sea posterior a inicio (HU-01)"""
        fecha_inicio = timezone.now() + timedelta(days=7)
        fecha_fin = fecha_inicio - timedelta(hours=1)  # Fecha inválida
        
        evento = Evento(
            nombre='Evento Inválido',
            descripcion='Descripción',
            tipo_evento=tipo_evento,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            lugar='Auditorio',
            cupo_maximo=100,
            costo=0,
            creado_por=usuario_organizador
        )
        
        with pytest.raises(ValidationError):
            evento.save()
    
    def test_cupos_disponibles(self, usuario_organizador, tipo_evento):
        """Test: Cálculo de cupos disponibles (HU-03)"""
        fecha_inicio = timezone.now() + timedelta(days=7)
        fecha_fin = fecha_inicio + timedelta(hours=3)
        
        evento = Evento.objects.create(
            nombre='Evento con Cupos',
            descripcion='Descripción',
            tipo_evento=tipo_evento,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            lugar='Auditorio',
            cupo_maximo=50,
            costo=0,
            creado_por=usuario_organizador
        )
        
        assert evento.cupos_disponibles == 50
        assert not evento.esta_lleno
        assert evento.porcentaje_ocupacion == 0
    
    def test_duplicar_evento(self, usuario_organizador, tipo_evento):
        """Test: Duplicar evento (HU-09)"""
        fecha_inicio = timezone.now() + timedelta(days=7)
        fecha_fin = fecha_inicio + timedelta(hours=3)
        
        evento_original = Evento.objects.create(
            nombre='Evento Original',
            descripcion='Descripción original',
            tipo_evento=tipo_evento,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            lugar='Auditorio',
            cupo_maximo=100,
            costo=50000,
            creado_por=usuario_organizador,
            estado='PUBLICADO'
        )
        
        evento_duplicado = evento_original.duplicar(usuario_organizador)
        
        assert evento_duplicado.nombre == 'Evento Original (Copia)'
        assert evento_duplicado.estado == 'BORRADOR'
        assert evento_duplicado.descripcion == evento_original.descripcion
        assert evento_duplicado.cupo_maximo == evento_original.cupo_maximo
        assert evento_duplicado.costo == evento_original.costo
    
    def test_estados_evento(self, usuario_organizador, tipo_evento):
        """Test: Cambio de estados del evento (HU-02, HU-06)"""
        fecha_inicio = timezone.now() + timedelta(days=7)
        fecha_fin = fecha_inicio + timedelta(hours=3)
        
        evento = Evento.objects.create(
            nombre='Evento de Estados',
            descripcion='Descripción',
            tipo_evento=tipo_evento,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            lugar='Auditorio',
            cupo_maximo=100,
            costo=0,
            creado_por=usuario_organizador
        )
        
        # Estado inicial
        assert evento.estado == 'BORRADOR'
        
        # Publicar evento
        evento.publicar(usuario_organizador)
        assert evento.estado == 'PUBLICADO'
        assert evento.esta_activo
        
        # Cancelar evento
        evento.cancelar(usuario_organizador)
        assert evento.estado == 'CANCELADO'
        assert not evento.esta_activo
    
    def test_evento_puede_inscribirse(self, usuario_organizador, tipo_evento):
        """Test: Verificar si permite inscripciones (HU-03)"""
        fecha_inicio = timezone.now() + timedelta(days=7)
        fecha_fin = fecha_inicio + timedelta(hours=3)
        
        evento = Evento.objects.create(
            nombre='Evento',
            descripcion='Descripción',
            tipo_evento=tipo_evento,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            lugar='Auditorio',
            cupo_maximo=10,
            costo=0,
            creado_por=usuario_organizador,
            estado='PUBLICADO'
        )
        
        assert evento.puede_inscribirse
        
        # Cambiar a estado finalizado
        evento.estado = 'FINALIZADO'
        evento.save()
        assert not evento.puede_inscribirse

