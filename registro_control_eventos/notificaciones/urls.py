"""
URLs para la aplicación de Notificaciones
"""

from django.urls import path
from . import views

app_name = 'notificaciones'

urlpatterns = [
    path('', views.lista_notificaciones, name='lista'),
    path('plantillas/', views.lista_plantillas, name='plantillas'),
    path('enviar/', views.enviar_notificacion, name='enviar'),
]

