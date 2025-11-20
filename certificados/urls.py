"""
URLs para la aplicación de Certificados
"""

from django.urls import path
from . import views

app_name = 'certificados'

urlpatterns = [
    path('', views.lista_certificados, name='lista'),
    path('generar-masivo/', views.generar_masivo, name='generar_masivo'),
    path('generar/<int:inscripcion_id>/', views.generar_certificado, name='generar'),
    path('enviar/<int:certificado_id>/', views.enviar_certificado, name='enviar'),
    path('verificar/<str:codigo>/', views.verificar_certificado, name='verificar'),
]

