"""
URLs para la aplicación de Notificaciones
"""

from django.urls import path
from . import views

app_name = 'notificaciones'

urlpatterns = [
    path('', views.lista_notificaciones, name='lista'),
    
    # Envío de notificaciones
    path('enviar/', views.enviar_notificacion_manual, name='enviar_manual'),
    path('<int:notificacion_id>/', views.detalle_notificacion, name='detalle'),
    
    # Plantillas
    path('plantillas/', views.lista_plantillas, name='plantillas'),
    path('plantillas/crear/', views.crear_plantilla, name='crear_plantilla'),
    path('plantillas/<int:plantilla_id>/editar/', views.editar_plantilla, name='editar_plantilla'),
    path('plantillas/<int:plantilla_id>/preview/', views.preview_plantilla, name='preview_plantilla'),
]
